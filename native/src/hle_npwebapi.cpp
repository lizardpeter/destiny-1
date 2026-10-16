// libSceNpWebApi: PSN web API requests, forwarded to the backend.
//
// A request names an API group (e.g. "sessionInvitation") and a path ("/v1/sessions"); the
// backend serves it at /npwebapi/<group><path>, so the PSN services the game uses can be
// answered there like the other online services. Without a backend every request fails
// with a network error, as it would offline.
//
// Handles: Initialize -> library context, CreateContext -> user context, CreateRequest ->
// 64-bit request id, CreateHandle / push event filters / callbacks -> small ids. Push events
// are never delivered.
#include <atomic>
#include <cstring>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <strings.h>

#include "hle.h"
#include "settings.h"

namespace d1 {
namespace {

constexpr int32_t kErrInvalidArgument = int32_t(0x80552902);
constexpr int32_t kErrRequestNotFound = int32_t(0x80552908);
constexpr int32_t kErrNotSent = int32_t(0x80552917);  // response read before send
constexpr int32_t kErrNetwork = int32_t(0x80552905);
constexpr int32_t kErrHeaderNotFound = int32_t(0x8055290d);

struct Request {
    std::string group, path, method, content_type;
    bool sent = false;
    BackendReply reply;
    size_t read_pos = 0;
};

std::mutex g_mutex;
std::map<int64_t, std::shared_ptr<Request>> g_requests;
std::atomic<int64_t> g_next_request{1};
std::atomic<int32_t> g_next_id{1};

std::shared_ptr<Request> find(int64_t id) {
    std::lock_guard lk(g_mutex);
    auto it = g_requests.find(id);
    return it == g_requests.end() ? nullptr : it->second;
}

const char* method_name(int32_t m) {
    switch (m) {
    case 0: return "GET";
    case 1: return "POST";
    case 2: return "PUT";
    case 3: return "DELETE";
    default: return "PATCH";
    }
}

struct ContentParameter {
    uint64_t content_length;
    const char* content_type;
    uint8_t reserved[16];
};

int32_t next_id() { return g_next_id++; }

int32_t sceNpWebApiInitialize(int32_t http_ctx, uint64_t pool) {
    log("npwebapi: initialize (http ctx %d, pool %#llx)", http_ctx, (unsigned long long)pool);
    return next_id();
}
int32_t sceNpWebApiTerminate(int32_t) { return SCE_OK; }
int32_t sceNpWebApiCreateContext(int32_t, const void*) { return next_id(); }
int32_t sceNpWebApiDeleteContext(int32_t) { return SCE_OK; }
int32_t sceNpWebApiCreateHandle(int32_t) { return next_id(); }
int32_t sceNpWebApiDeleteHandle(int32_t, int32_t) { return SCE_OK; }
int32_t sceNpWebApiCreatePushEventFilter(int32_t, const void*, uint64_t) { return next_id(); }
int32_t sceNpWebApiDeletePushEventFilter(int32_t, int32_t) { return SCE_OK; }
int32_t sceNpWebApiCreateServicePushEventFilter(int32_t, int32_t, const char*, uint32_t, const void*, uint64_t) {
    return next_id();
}
int32_t sceNpWebApiDeleteServicePushEventFilter(int32_t, int32_t) { return SCE_OK; }
int32_t sceNpWebApiRegisterPushEventCallback(int32_t, int32_t, void*, void*) { return next_id(); }
int32_t sceNpWebApiUnregisterPushEventCallback(int32_t, int32_t) { return SCE_OK; }
int32_t sceNpWebApiRegisterServicePushEventCallback(int32_t, int32_t, void*, void*) { return next_id(); }
int32_t sceNpWebApiUnregisterServicePushEventCallback(int32_t, int32_t) { return SCE_OK; }

int32_t sceNpWebApiCreateRequest(int32_t user_ctx, const char* group, const char* path, int32_t method,
                                 const ContentParameter* content, int64_t* request_id) {
    if (!group || !path || !request_id) return kErrInvalidArgument;
    auto r = std::make_shared<Request>();
    r->group = group;
    r->path = path;
    r->method = method_name(method);
    if (content && content->content_type) r->content_type = content->content_type;
    const int64_t id = g_next_request++;
    {
        std::lock_guard lk(g_mutex);
        g_requests[id] = r;
    }
    *request_id = id;
    return SCE_OK;
}
int32_t sceNpWebApiDeleteRequest(int64_t id) {
    std::lock_guard lk(g_mutex);
    return g_requests.erase(id) ? SCE_OK : kErrRequestNotFound;
}
int32_t sceNpWebApiAbortRequest(int64_t) { return SCE_OK; }

int32_t sceNpWebApiSendRequest(int64_t id, const void* data, uint64_t size) {
    auto r = find(id);
    if (!r) return kErrRequestNotFound;
    std::vector<std::pair<std::string, std::string>> headers;
    if (!r->content_type.empty()) headers.push_back({"Content-Type", r->content_type});
    headers.push_back({"X-D1-NpWebApi-Group", r->group});
    // the user's PSN access token, as libSceNpWebApi sends it (the backend's caller identity)
    headers.push_back({"Authorization", "Bearer d1b-D1NATIVE-" + settings().name});
    const std::string host = r->group + ".np.playstation.net";
    if (!backend_http(r->method, host, "/npwebapi/" + r->group + r->path, headers, data, size_t(size), r->reply)) {
        log("npwebapi: %s %s%s -> backend unreachable", r->method.c_str(), r->group.c_str(), r->path.c_str());
        return kErrNetwork;
    }
    r->sent = true;
    log("npwebapi: %s %s%s (%llu bytes) -> %d (%zu bytes)", r->method.c_str(), r->group.c_str(), r->path.c_str(),
        (unsigned long long)size, r->reply.status, r->reply.body.size());
    return SCE_OK;
}

int32_t sceNpWebApiGetHttpStatusCode(int64_t id, int32_t* code) {
    auto r = find(id);
    if (!r) return kErrRequestNotFound;
    if (!r->sent) return kErrNotSent;
    if (code) *code = r->reply.status;
    return SCE_OK;
}

int32_t sceNpWebApiReadData(int64_t id, void* buf, uint64_t size) {
    auto r = find(id);
    if (!r) return kErrRequestNotFound;
    if (!r->sent) return kErrNotSent;
    const size_t n = std::min<size_t>(size_t(size), r->reply.body.size() - r->read_pos);
    if (n) std::memcpy(buf, r->reply.body.data() + r->read_pos, n);
    r->read_pos += n;
    return int32_t(n);
}

const std::string* header(const Request& r, const char* name) {
    for (auto& [k, v] : r.reply.headers)
        if (name && strcasecmp(k.c_str(), name) == 0) return &v;
    return nullptr;
}
int32_t sceNpWebApiGetHttpResponseHeaderValueLength(int64_t id, const char* name, uint64_t* len) {
    auto r = find(id);
    if (!r) return kErrRequestNotFound;
    const std::string* v = header(*r, name);
    if (!v) return kErrHeaderNotFound;
    if (len) *len = v->size();
    return SCE_OK;
}
int32_t sceNpWebApiGetHttpResponseHeaderValue(int64_t id, const char* name, char* out, uint64_t size) {
    auto r = find(id);
    if (!r) return kErrRequestNotFound;
    const std::string* v = header(*r, name);
    if (!v) return kErrHeaderNotFound;
    if (out && size) {
        const size_t n = std::min<size_t>(v->size(), size_t(size) - 1);
        std::memcpy(out, v->data(), n);
        out[n] = 0;
    }
    return SCE_OK;
}

// SceNpId: online id (16 chars + terminator, padded to 20) followed by opt/reserved bytes.
int32_t sceNpWebApiUtilityParseNpId(const char* json, void* npid) {
    if (!npid) return kErrInvalidArgument;
    std::memset(npid, 0, 36);
    if (json) {
        // accept either a bare online id or {"onlineId":"..."}
        std::string s = json;
        if (auto p = s.find("\"onlineId\""); p != std::string::npos) {
            auto a = s.find('"', s.find(':', p) + 1), b = a == std::string::npos ? a : s.find('"', a + 1);
            s = (a != std::string::npos && b != std::string::npos) ? s.substr(a + 1, b - a - 1) : "";
        }
        std::strncpy(static_cast<char*>(npid), s.c_str(), 16);
    }
    return SCE_OK;
}

}  // namespace

HLE("sceNpWebApiInitialize", sceNpWebApiInitialize)
HLE("sceNpWebApiTerminate", sceNpWebApiTerminate)
HLE("sceNpWebApiCreateContext", sceNpWebApiCreateContext)
HLE("sceNpWebApiDeleteContext", sceNpWebApiDeleteContext)
HLE("sceNpWebApiCreateHandle", sceNpWebApiCreateHandle)
HLE("sceNpWebApiDeleteHandle", sceNpWebApiDeleteHandle)
HLE("sceNpWebApiCreatePushEventFilter", sceNpWebApiCreatePushEventFilter)
HLE("sceNpWebApiDeletePushEventFilter", sceNpWebApiDeletePushEventFilter)
HLE("sceNpWebApiCreateServicePushEventFilter", sceNpWebApiCreateServicePushEventFilter)
HLE("sceNpWebApiDeleteServicePushEventFilter", sceNpWebApiDeleteServicePushEventFilter)
HLE("sceNpWebApiRegisterPushEventCallback", sceNpWebApiRegisterPushEventCallback)
HLE("sceNpWebApiUnregisterPushEventCallback", sceNpWebApiUnregisterPushEventCallback)
HLE("sceNpWebApiRegisterServicePushEventCallback", sceNpWebApiRegisterServicePushEventCallback)
HLE("sceNpWebApiUnregisterServicePushEventCallback", sceNpWebApiUnregisterServicePushEventCallback)
HLE("sceNpWebApiCreateRequest", sceNpWebApiCreateRequest)
HLE("sceNpWebApiDeleteRequest", sceNpWebApiDeleteRequest)
HLE("sceNpWebApiAbortRequest", sceNpWebApiAbortRequest)
HLE("sceNpWebApiSendRequest", sceNpWebApiSendRequest)
HLE("sceNpWebApiGetHttpStatusCode", sceNpWebApiGetHttpStatusCode)
HLE("sceNpWebApiReadData", sceNpWebApiReadData)
HLE("sceNpWebApiGetHttpResponseHeaderValueLength", sceNpWebApiGetHttpResponseHeaderValueLength)
HLE("sceNpWebApiGetHttpResponseHeaderValue", sceNpWebApiGetHttpResponseHeaderValue)
HLE("sceNpWebApiUtilityParseNpId", sceNpWebApiUtilityParseNpId)

}  // namespace d1
