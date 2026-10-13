// libSceHttp / libSceSsl. Requests to the services the backend replaces (see
// backend_route in hle_net.cpp) are sent as plain HTTP/1.1 to the D1_BACKEND server, on
// port D1_BACKEND_HTTP_PORT (default 8080), with the original Host header, so the backend
// sees which service was addressed. TLS is never used: libSceHttp is ours, so the game
// cannot tell. Every other request fails as a DNS error, like a console with no route out.
#include "net_compat.h"

#include <atomic>
#include <cctype>
#include <cstdlib>
#include <cstring>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "hle.h"

namespace d1 {

constexpr int32_t kHttpErrNoDns = int32_t(0x80436002);       // ORBIS_HTTP_ERROR_RESOLVER_ENODNS
constexpr int32_t kHttpErrBeforeSend = int32_t(0x80431065);  // ORBIS_HTTP_ERROR_BEFORE_SEND
constexpr int32_t kHttpErrInvalidUrl = int32_t(0x80433060);
constexpr int32_t kHttpErrNoMemory = int32_t(0x80431022);
constexpr int32_t kHttpErrNetwork = int32_t(0x80431063);     // ORBIS_HTTP_ERROR_NETWORK
constexpr int32_t kHttpErrInvalidId = int32_t(0x80431100);

using Headers = std::vector<std::pair<std::string, std::string>>;

struct HttpObj {
    enum Kind { Template, Connection, Request } kind;
    int32_t parent = 0;
    Headers headers;                 // added at this level
    std::string scheme, host, path;  // connection: scheme/host/port; request: path
    uint16_t port = 0;
    std::string method;
    uint64_t content_length = 0;
    // response
    bool sent = false;
    int32_t status = 0;
    Headers resp_headers;
    std::string body;
    size_t read_pos = 0;
};

static std::mutex g_http_mutex;
static std::atomic<int32_t> g_http_id{1};
static std::map<int32_t, std::shared_ptr<HttpObj>> g_http;

static std::shared_ptr<HttpObj> obj(int32_t id) {
    std::lock_guard lk(g_http_mutex);
    auto it = g_http.find(id);
    return it == g_http.end() ? nullptr : it->second;
}
static int32_t add(std::shared_ptr<HttpObj> o) {
    int32_t id = g_http_id++;
    std::lock_guard lk(g_http_mutex);
    g_http[id] = std::move(o);
    return id;
}

// "https://host:port/path?q" -> parts
static bool split_url(const std::string& url, std::string& scheme, std::string& host, uint16_t& port,
                      std::string& path) {
    size_t p = url.find("://");
    if (p == std::string::npos) return false;
    scheme = url.substr(0, p);
    size_t h = p + 3, slash = url.find('/', h);
    std::string auth = url.substr(h, slash == std::string::npos ? std::string::npos : slash - h);
    path = slash == std::string::npos ? "/" : url.substr(slash);
    size_t c = auth.rfind(':');
    if (c != std::string::npos) {
        port = uint16_t(std::atoi(auth.c_str() + c + 1));
        host = auth.substr(0, c);
    } else {
        port = scheme == "https" ? 443 : 80;
        host = auth;
    }
    return !host.empty();
}

static const char* kMethods[] = {"GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE", "TRACE", "CONNECT"};

static int32_t sceSslInit(uint64_t) { return 1; }
HLE("sceSslInit", sceSslInit)
static int32_t sceSslTerm(int32_t) { return SCE_OK; }
HLE("sceSslTerm", sceSslTerm)
static int32_t sceHttpInit(int32_t, int32_t, uint64_t) { return g_http_id++; }
HLE("sceHttpInit", sceHttpInit)
static int32_t sceHttpTerm(int32_t) { return SCE_OK; }
HLE("sceHttpTerm", sceHttpTerm)

static int32_t sceHttpCreateTemplate(int32_t, const char* ua, int32_t, int32_t) {
    auto o = std::make_shared<HttpObj>();
    o->kind = HttpObj::Template;
    if (ua) o->headers.push_back({"User-Agent", ua});
    return add(o);
}
HLE("sceHttpCreateTemplate", sceHttpCreateTemplate)
static int32_t sceHttpCreateConnection(int32_t tmpl, const char* host, const char* scheme, uint16_t port, int32_t) {
    auto o = std::make_shared<HttpObj>();
    o->kind = HttpObj::Connection;
    o->parent = tmpl;
    o->host = host ? host : "";
    o->scheme = scheme ? scheme : "http";
    o->port = port;
    return add(o);
}
HLE("sceHttpCreateConnection", sceHttpCreateConnection)
static int32_t sceHttpCreateConnectionWithURL(int32_t tmpl, const char* url, bool) {
    auto o = std::make_shared<HttpObj>();
    o->kind = HttpObj::Connection;
    o->parent = tmpl;
    std::string path;
    if (!url || !split_url(url, o->scheme, o->host, o->port, path)) return kHttpErrInvalidUrl;
    return add(o);
}
HLE("sceHttpCreateConnectionWithURL", sceHttpCreateConnectionWithURL)
static int32_t sceHttpCreateRequestWithURL(int32_t conn, int32_t method, const char* url, uint64_t len) {
    auto o = std::make_shared<HttpObj>();
    o->kind = HttpObj::Request;
    o->parent = conn;
    o->method = (method >= 0 && method < 8) ? kMethods[method] : "GET";
    o->content_length = len;
    if (!url || !split_url(url, o->scheme, o->host, o->port, o->path)) return kHttpErrInvalidUrl;
    return add(o);
}
HLE("sceHttpCreateRequestWithURL", sceHttpCreateRequestWithURL)
static int32_t sceHttpCreateRequest2(int32_t conn, const char* method, const char* path, uint64_t len) {
    auto c = obj(conn);
    if (!c) return kHttpErrInvalidId;
    auto o = std::make_shared<HttpObj>();
    o->kind = HttpObj::Request;
    o->parent = conn;
    o->method = method ? method : "GET";
    o->scheme = c->scheme, o->host = c->host, o->port = c->port;
    o->path = path && *path ? path : "/";
    o->content_length = len;
    return add(o);
}
HLE("sceHttpCreateRequest2", sceHttpCreateRequest2)

static int32_t sceHttpAddRequestHeader(int32_t id, const char* name, const char* value, uint32_t mode) {
    auto o = obj(id);
    if (!o || !name) return kHttpErrInvalidId;
    std::lock_guard lk(g_http_mutex);
    if (mode == 0)  // overwrite
        for (auto it = o->headers.begin(); it != o->headers.end();)
            it = strcasecmp(it->first.c_str(), name) == 0 ? o->headers.erase(it) : it + 1;
    o->headers.push_back({name, value ? value : ""});
    return SCE_OK;
}
HLE("sceHttpAddRequestHeader", sceHttpAddRequestHeader)
static int32_t sceHttpRemoveRequestHeader(int32_t id, const char* name) {
    auto o = obj(id);
    if (!o || !name) return kHttpErrInvalidId;
    std::lock_guard lk(g_http_mutex);
    for (auto it = o->headers.begin(); it != o->headers.end();)
        it = strcasecmp(it->first.c_str(), name) == 0 ? o->headers.erase(it) : it + 1;
    return SCE_OK;
}
HLE("sceHttpRemoveRequestHeader", sceHttpRemoveRequestHeader)
static int32_t sceHttpSetRequestContentLength(int32_t id, uint64_t len) {
    if (auto o = obj(id)) o->content_length = len;
    return SCE_OK;
}
HLE("sceHttpSetRequestContentLength", sceHttpSetRequestContentLength)

// Blocking HTTP/1.1 exchange with the backend; the whole response is buffered.
static bool exchange(uint32_t addr, uint16_t port, const std::string& req, HttpObj& r) {
    int fd = int(socket(AF_INET, SOCK_STREAM, 0));
    if (fd < 0) return false;
    net::set_timeouts(fd, 30);
    sockaddr_in sa{};
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);
    sa.sin_addr.s_addr = addr;
    if (connect(fd, reinterpret_cast<sockaddr*>(&sa), sizeof sa) != 0) {
        net::close(fd);
        return false;
    }
    for (size_t off = 0; off < req.size();) {
        auto n = send(fd, req.data() + off, int(req.size() - off), MSG_NOSIGNAL);
        if (n <= 0) { net::close(fd); return false; }
        off += size_t(n);
    }
    std::string raw;
    char buf[16384];
    for (int n; (n = int(recv(fd, buf, sizeof buf, 0))) > 0;) raw.append(buf, size_t(n));
    net::close(fd);
    size_t hdr_end = raw.find("\r\n\r\n");
    if (hdr_end == std::string::npos || raw.compare(0, 5, "HTTP/") != 0) return false;
    r.status = std::atoi(raw.c_str() + raw.find(' ') + 1);
    bool chunked = false;
    for (size_t p = raw.find("\r\n") + 2; p < hdr_end;) {
        size_t e = raw.find("\r\n", p), c = raw.find(':', p);
        if (c != std::string::npos && c < e) {
            std::string k = raw.substr(p, c - p), v = raw.substr(c + 1, e - c - 1);
            while (!v.empty() && v[0] == ' ') v.erase(0, 1);
            if (strcasecmp(k.c_str(), "Transfer-Encoding") == 0 && v.find("chunked") != std::string::npos) chunked = true;
            r.resp_headers.push_back({k, v});
        }
        p = e + 2;
    }
    std::string body = raw.substr(hdr_end + 4);
    if (chunked) {
        std::string out;
        for (size_t p = 0; p < body.size();) {
            size_t e = body.find("\r\n", p);
            if (e == std::string::npos) break;
            size_t n = std::strtoul(body.c_str() + p, nullptr, 16);
            if (n == 0) break;
            out.append(body, e + 2, n);
            p = e + 2 + n + 2;
        }
        body = std::move(out);
    }
    r.body = std::move(body);
    return true;
}

static int32_t sceHttpSendRequest(int32_t id, const void* data, uint64_t size) {
    auto r = obj(id);
    if (!r || r->kind != HttpObj::Request) return kHttpErrInvalidId;
    const std::string url = r->scheme + "://" + r->host + ":" + std::to_string(r->port) + r->path;
    uint32_t addr;
    if (!backend_route(r->host.c_str(), &addr)) {
        log("http: %s %s not sent (no backend for this host)", r->method.c_str(), url.c_str());
        return kHttpErrNoDns;
    }
    // headers: template, then connection, then request (later levels override)
    Headers hs;
    {
        std::lock_guard lk(g_http_mutex);
        std::vector<HttpObj*> chain{r.get()};
        for (int32_t p = r->parent; p;) {
            auto it = g_http.find(p);
            if (it == g_http.end()) break;
            chain.push_back(it->second.get());
            p = it->second->parent;
        }
        for (auto it = chain.rbegin(); it != chain.rend(); ++it)
            for (auto& h : (*it)->headers) {
                for (auto x = hs.begin(); x != hs.end();)
                    x = strcasecmp(x->first.c_str(), h.first.c_str()) == 0 ? hs.erase(x) : x + 1;
                hs.push_back(h);
            }
    }
    std::string req = r->method + " " + r->path + " HTTP/1.1\r\nHost: " + r->host + "\r\n";
    req += "X-D1-Original-URL: " + url + "\r\n";
    for (auto& [k, v] : hs)
        if (strcasecmp(k.c_str(), "Host") && strcasecmp(k.c_str(), "Content-Length") && strcasecmp(k.c_str(), "Connection"))
            req += k + ": " + v + "\r\n";
    req += "Content-Length: " + std::to_string(data ? size : 0) + "\r\nConnection: close\r\n\r\n";
    if (data && size) req.append(static_cast<const char*>(data), size);

    static const uint16_t port = [] {
        const char* p = getenv("D1_BACKEND_HTTP_PORT");
        return uint16_t(p ? std::atoi(p) : 8080);
    }();
    if (!exchange(addr, port, req, *r)) {
        log("http: %s %s -> backend %s:%u unreachable", r->method.c_str(), url.c_str(), backend_host(), port);
        return kHttpErrNetwork;
    }
    r->sent = true;
    log("http: %s %s -> %d (%zu bytes)", r->method.c_str(), url.c_str(), r->status, r->body.size());
    return SCE_OK;
}
HLE("sceHttpSendRequest", sceHttpSendRequest)

// One request to the backend's HTTP port from other HLE modules (NpWebApi).
bool backend_http(const std::string& method, const std::string& host, const std::string& path,
                  const std::vector<std::pair<std::string, std::string>>& headers, const void* data,
                  size_t size, BackendReply& out) {
    uint32_t addr;
    if (!backend_route(host.c_str(), &addr)) return false;
    std::string req = method + " " + path + " HTTP/1.1\r\nHost: " + host + "\r\n";
    for (auto& [k, v] : headers)
        if (strcasecmp(k.c_str(), "Host") && strcasecmp(k.c_str(), "Content-Length") && strcasecmp(k.c_str(), "Connection"))
            req += k + ": " + v + "\r\n";
    req += "Content-Length: " + std::to_string(data ? size : 0) + "\r\nConnection: close\r\n\r\n";
    if (data && size) req.append(static_cast<const char*>(data), size);
    static const uint16_t port = [] {
        const char* p = getenv("D1_BACKEND_HTTP_PORT");
        return uint16_t(p ? std::atoi(p) : 8080);
    }();
    HttpObj r{HttpObj::Request};
    if (!exchange(addr, port, req, r)) return false;
    out.status = r.status;
    out.headers = std::move(r.resp_headers);
    out.body = std::move(r.body);
    return true;
}

static int32_t sceHttpGetStatusCode(int32_t id, int32_t* status) {
    auto r = obj(id);
    if (!r || !r->sent) return kHttpErrBeforeSend;
    if (status) *status = r->status;
    return SCE_OK;
}
HLE("sceHttpGetStatusCode", sceHttpGetStatusCode)
static int32_t sceHttpGetResponseContentLength(int32_t id, int32_t* result, uint64_t* len) {
    auto r = obj(id);
    if (!r || !r->sent) return kHttpErrBeforeSend;
    if (result) *result = 0;  // 0 = length known
    if (len) *len = r->body.size();
    return SCE_OK;
}
HLE("sceHttpGetResponseContentLength", sceHttpGetResponseContentLength)
static int32_t sceHttpReadData(int32_t id, void* buf, uint64_t size) {
    auto r = obj(id);
    if (!r || !r->sent) return kHttpErrBeforeSend;
    size_t n = std::min<size_t>(size, r->body.size() - r->read_pos);
    std::memcpy(buf, r->body.data() + r->read_pos, n);
    r->read_pos += n;
    return int32_t(n);
}
HLE("sceHttpReadData", sceHttpReadData)
static int32_t http_delete(int32_t id) {
    std::lock_guard lk(g_http_mutex);
    g_http.erase(id);
    return SCE_OK;
}
HLE("sceHttpDeleteRequest", http_delete)
HLE("sceHttpDeleteConnection", http_delete)
HLE("sceHttpDeleteTemplate", http_delete)
static int32_t http_ok() { return SCE_OK; }
HLE("sceHttpAbortRequest", http_ok)
HLE("sceHttpSetChunkedTransferEnabled", http_ok)
HLE("sceHttpSetConnectTimeOut", http_ok)
HLE("sceHttpSetResolveRetry", http_ok)
HLE("sceHttpsLoadCert", http_ok)
HLE("sceHttpsSetSslCallback", http_ok)

// ------------------------------------------------------------------ URI helpers
struct UriElement {
    bool opaque;
    char* scheme;
    char* username;
    char* password;
    char* hostname;
    char* path;
    char* query;
    char* fragment;
    uint16_t port;
    uint8_t reserved[10];
};

static int32_t sceHttpUriParse(UriElement* out, const char* uri, void* pool, uint64_t* require, uint64_t prepare) {
    if (!uri) return kHttpErrInvalidUrl;
    std::string s(uri), scheme, user, pass, host, path, query, frag;
    uint16_t port = 0;
    bool opaque = true;
    size_t pos = 0;
    size_t c = s.find(':');
    if (c != std::string::npos && c > 0 && std::isalpha(uint8_t(s[0]))) {
        bool ok = true;
        for (size_t i = 0; i < c; ++i) ok &= std::isalnum(uint8_t(s[i])) || s[i] == '+' || s[i] == '-' || s[i] == '.';
        if (ok) { scheme = s.substr(0, c); pos = c + 1; }
    }
    if (s.compare(pos, 2, "//") == 0) {
        opaque = false;
        pos += 2;
        size_t end = s.find_first_of("/?#", pos);
        std::string auth = s.substr(pos, end == std::string::npos ? std::string::npos : end - pos);
        pos = end == std::string::npos ? s.size() : end;
        size_t at = auth.rfind('@');
        if (at != std::string::npos) {
            std::string ui = auth.substr(0, at);
            auth = auth.substr(at + 1);
            size_t pc = ui.find(':');
            user = ui.substr(0, pc);
            if (pc != std::string::npos) pass = ui.substr(pc + 1);
        }
        size_t pc = auth.rfind(':');
        if (pc != std::string::npos && auth.find(']') == std::string::npos) {
            port = uint16_t(std::atoi(auth.c_str() + pc + 1));
            auth = auth.substr(0, pc);
        }
        host = auth;
    }
    size_t q = s.find('?', pos), h = s.find('#', pos);
    path = s.substr(pos, std::min(q, h) - pos);
    if (q != std::string::npos) query = s.substr(q, (h == std::string::npos ? s.size() : h) - q);
    if (h != std::string::npos) frag = s.substr(h);
    if (!port) port = scheme == "https" ? 443 : scheme == "http" ? 80 : 0;

    const std::string* parts[] = {&scheme, &user, &pass, &host, &path, &query, &frag};
    uint64_t need = 0;
    for (auto* p : parts) need += p->size() + 1;
    if (require) *require = need;
    if (!out || !pool) return SCE_OK;
    if (prepare < need) return kHttpErrNoMemory;
    char* w = static_cast<char*>(pool);
    char** slots[] = {&out->scheme, &out->username, &out->password, &out->hostname, &out->path, &out->query, &out->fragment};
    std::memset(out, 0, sizeof *out);
    for (int i = 0; i < 7; ++i) {
        std::memcpy(w, parts[i]->c_str(), parts[i]->size() + 1);
        *slots[i] = w;
        w += parts[i]->size() + 1;
    }
    out->opaque = opaque;
    out->port = port;
    return SCE_OK;
}
HLE("sceHttpUriParse", sceHttpUriParse)

static int32_t sceHttpUriEscape(char* out, uint64_t* require, uint64_t prepare, const char* in) {
    if (!in) return kHttpErrInvalidUrl;
    std::string r;
    static const char* hex = "0123456789ABCDEF";
    for (const char* p = in; *p; ++p) {
        uint8_t ch = uint8_t(*p);
        if (std::isalnum(ch) || std::strchr("-_.~", ch)) r.push_back(char(ch));
        else { r.push_back('%'); r.push_back(hex[ch >> 4]); r.push_back(hex[ch & 15]); }
    }
    if (require) *require = r.size() + 1;
    if (!out) return SCE_OK;
    if (prepare < r.size() + 1) return kHttpErrNoMemory;
    std::memcpy(out, r.c_str(), r.size() + 1);
    return SCE_OK;
}
HLE("sceHttpUriEscape", sceHttpUriEscape)

}  // namespace d1
