// libSceHttp / libSceSsl: object bookkeeping and URI helpers. Requests are never sent;
// SendRequest logs the URL and fails with a DNS error, like a console with no route out.
#include <atomic>
#include <cctype>
#include <cstring>
#include <map>
#include <mutex>
#include <string>

#include "hle.h"

namespace d1 {

constexpr int32_t kHttpErrNoDns = int32_t(0x80436002);       // ORBIS_HTTP_ERROR_RESOLVER_ENODNS
constexpr int32_t kHttpErrBeforeSend = int32_t(0x80431065);  // ORBIS_HTTP_ERROR_BEFORE_SEND
constexpr int32_t kHttpErrInvalidUrl = int32_t(0x80433060);
constexpr int32_t kHttpErrNoMemory = int32_t(0x80431022);

static std::mutex g_http_mutex;
static std::atomic<int32_t> g_http_id{1};
static std::map<int32_t, std::string> g_urls;  // connection / request id -> URL or host

static int32_t sceSslInit(uint64_t) { return 1; }
HLE("sceSslInit", sceSslInit)
static int32_t sceSslTerm(int32_t) { return SCE_OK; }
HLE("sceSslTerm", sceSslTerm)
static int32_t sceHttpInit(int32_t, int32_t, uint64_t) { return g_http_id++; }
HLE("sceHttpInit", sceHttpInit)
static int32_t sceHttpTerm(int32_t) { return SCE_OK; }
HLE("sceHttpTerm", sceHttpTerm)
static int32_t sceHttpCreateTemplate(int32_t, const char* ua, int32_t, int32_t) { return g_http_id++; }
HLE("sceHttpCreateTemplate", sceHttpCreateTemplate)
static int32_t sceHttpCreateConnection(int32_t, const char* host, const char* scheme, uint16_t port, int32_t) {
    int32_t id = g_http_id++;
    std::lock_guard lk(g_http_mutex);
    g_urls[id] = std::string(scheme ? scheme : "http") + "://" + (host ? host : "?") + ":" + std::to_string(port);
    return id;
}
HLE("sceHttpCreateConnection", sceHttpCreateConnection)
static int32_t sceHttpCreateConnectionWithURL(int32_t, const char* url, bool) {
    int32_t id = g_http_id++;
    std::lock_guard lk(g_http_mutex);
    g_urls[id] = url ? url : "";
    return id;
}
HLE("sceHttpCreateConnectionWithURL", sceHttpCreateConnectionWithURL)
static int32_t sceHttpCreateRequestWithURL(int32_t, int32_t method, const char* url, uint64_t) {
    int32_t id = g_http_id++;
    std::lock_guard lk(g_http_mutex);
    g_urls[id] = url ? url : "";
    return id;
}
HLE("sceHttpCreateRequestWithURL", sceHttpCreateRequestWithURL)
static int32_t sceHttpCreateRequest2(int32_t conn, const char* method, const char* path, uint64_t) {
    int32_t id = g_http_id++;
    std::lock_guard lk(g_http_mutex);
    g_urls[id] = std::string(method ? method : "?") + " " + g_urls[conn] + (path ? path : "");
    return id;
}
HLE("sceHttpCreateRequest2", sceHttpCreateRequest2)
static int32_t sceHttpSendRequest(int32_t req, const void*, uint64_t size) {
    std::lock_guard lk(g_http_mutex);
    log("http: request %d not sent (no external network): %s (%lu bytes body)", req, g_urls[req].c_str(), size);
    return kHttpErrNoDns;
}
HLE("sceHttpSendRequest", sceHttpSendRequest)
static int32_t sceHttpGetStatusCode(int32_t, int32_t*) { return kHttpErrBeforeSend; }
HLE("sceHttpGetStatusCode", sceHttpGetStatusCode)
static int32_t sceHttpGetResponseContentLength(int32_t, int32_t*, uint64_t*) { return kHttpErrBeforeSend; }
HLE("sceHttpGetResponseContentLength", sceHttpGetResponseContentLength)
static int32_t sceHttpReadData(int32_t, void*, uint64_t) { return kHttpErrBeforeSend; }
HLE("sceHttpReadData", sceHttpReadData)
static int32_t http_ok() { return SCE_OK; }
HLE("sceHttpAbortRequest", http_ok)
HLE("sceHttpDeleteRequest", http_ok)
HLE("sceHttpDeleteConnection", http_ok)
HLE("sceHttpDeleteTemplate", http_ok)
HLE("sceHttpAddRequestHeader", http_ok)
HLE("sceHttpRemoveRequestHeader", http_ok)
HLE("sceHttpSetRequestContentLength", http_ok)
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
