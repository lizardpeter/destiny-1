// Discord Rich Presence through Discord's local IPC socket (the protocol Discord's own
// RPC libraries use): connect to discord-ipc-N, send a handshake with the application id,
// then SET_ACTIVITY frames. Same design as Rust-test's presence worker: one background
// thread owns the connection, the game never blocks on it, and every failure is ignored
// (retry later). Named pipe on Windows, Unix socket on Linux.
#include "discord.h"

#include "os.h"
#if D1_WINDOWS
#define NOMINMAX
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#endif

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>

#include "hle.h"
#include "settings.h"

namespace d1 {
namespace {

std::string json_escape(const std::string& s) {
    std::string o;
    for (char c : s) {
        if (c == '"' || c == '\\') o += '\\';
        if (static_cast<unsigned char>(c) < 0x20) continue;
        o += c;
    }
    return o;
}

// Discord's IPC endpoint: \\.\pipe\discord-ipc-N on Windows, a Unix socket elsewhere.
class Ipc {
public:
    ~Ipc() { close_fd(); }
    bool connected() const { return open_; }

    bool connect_any(const std::string& app_id) {
        for (const std::string& path : candidates()) {
            if (!open_path(path)) continue;
            if (send(0, "{\"v\":1,\"client_id\":\"" + json_escape(app_id) + "\"}") && read_frame()) {
                log("discord: connected (%s)", path.c_str());
                return true;
            }
            close_fd();
        }
        return false;
    }

    bool set_activity(const std::string& activity_json) {
        static uint64_t nonce = 0;
        std::string msg = "{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":" + std::to_string(pid()) +
                          ",\"activity\":" + activity_json + "},\"nonce\":\"" + std::to_string(++nonce) + "\"}";
        if (!send(1, msg) || !read_frame()) {
            close_fd();
            return false;
        }
        return true;
    }

private:
#if D1_WINDOWS
    static std::vector<std::string> candidates() {
        std::vector<std::string> v;
        for (int i = 0; i < 10; ++i) v.push_back("\\\\.\\pipe\\discord-ipc-" + std::to_string(i));
        return v;
    }
    static uint32_t pid() { return GetCurrentProcessId(); }
    bool open_path(const std::string& path) {
        h_ = CreateFileA(path.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
        open_ = h_ != INVALID_HANDLE_VALUE;
        return open_;
    }
    bool write_all(const char* p, size_t n) {
        DWORD put = 0;
        return WriteFile(h_, p, DWORD(n), &put, nullptr) && put == n;
    }
    bool read_exact(char* p, size_t n) {  // waits at most ~2 s for Discord to answer
        for (int waited = 0; n;) {
            DWORD avail = 0;
            if (!PeekNamedPipe(h_, nullptr, 0, nullptr, &avail, nullptr)) return false;
            if (!avail) {
                if (++waited > 200) return false;
                Sleep(10);
                continue;
            }
            DWORD got = 0;
            if (!ReadFile(h_, p, DWORD(std::min<size_t>(n, avail)), &got, nullptr) || !got) return false;
            p += got;
            n -= got;
        }
        return true;
    }
    void close_fd() {
        if (open_) CloseHandle(h_);
        open_ = false;
    }
    HANDLE h_ = INVALID_HANDLE_VALUE;
#else
    static std::vector<std::string> candidates() {
        const char* xdg = getenv("XDG_RUNTIME_DIR");
        std::string dirs[] = {
            xdg ? xdg : "",
            xdg ? std::string(xdg) + "/app/com.discordapp.Discord" : "",
            xdg ? std::string(xdg) + "/snap.discord" : "",
            getenv("TMPDIR") ? getenv("TMPDIR") : "",
            "/tmp",
        };
        std::vector<std::string> v;
        for (auto& d : dirs)
            if (!d.empty())
                for (int i = 0; i < 10; ++i) v.push_back(d + "/discord-ipc-" + std::to_string(i));
        return v;
    }
    static uint32_t pid() { return uint32_t(getpid()); }
    bool open_path(const std::string& path) {
        int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
        if (fd < 0) return false;
        sockaddr_un sa{};
        sa.sun_family = AF_UNIX;
        std::strncpy(sa.sun_path, path.c_str(), sizeof sa.sun_path - 1);
        if (::connect(fd, reinterpret_cast<sockaddr*>(&sa), sizeof sa) != 0) {
            ::close(fd);
            return false;
        }
        timeval tv{2, 0};
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
        fd_ = fd;
        open_ = true;
        return true;
    }
    bool write_all(const char* p, size_t n) {
        while (n) {
            ssize_t k = ::send(fd_, p, n, MSG_NOSIGNAL);
            if (k <= 0) return false;
            p += k;
            n -= size_t(k);
        }
        return true;
    }
    bool read_exact(char* p, size_t n) { return n == 0 || recv(fd_, p, n, MSG_WAITALL) == ssize_t(n); }
    void close_fd() {
        if (open_) ::close(fd_);
        open_ = false;
        fd_ = -1;
    }
    int fd_ = -1;
#endif
    bool send(uint32_t op, const std::string& json) {
        std::string frame(8, '\0');
        uint32_t len = uint32_t(json.size());
        std::memcpy(frame.data(), &op, 4);
        std::memcpy(frame.data() + 4, &len, 4);
        frame += json;
        return open_ && write_all(frame.data(), frame.size());
    }
    bool read_frame() {  // reply contents are not needed; just keep the stream in sync
        uint32_t hdr[2];
        if (!read_exact(reinterpret_cast<char*>(hdr), 8) || hdr[1] > (1u << 20)) return false;
        std::string body(hdr[1], '\0');
        return read_exact(body.data(), hdr[1]);
    }
    bool open_ = false;
};

// Player-facing text for the world-controller state.
std::string describe(const char* state) {
    if (!state) return "Starting up";
    std::string s = state;
    if (s == "bootflow:media_check" || s == "bootflow:bootload" || s == "bootflow:intro_screen_display" ||
        s == "bootflow:start")
        return "At the title screen";
    if (s.rfind("bootflow:", 0) == 0 || s == "cleanup") return "Signing in";
    if (s.rfind("character:", 0) == 0) return "Choosing a Guardian";
    if (s == "setup:orbit" || s == "setup:orbit_loading" || s == "setup:orbit_outro") return "In orbit";
    if (s.rfind("setup:", 0) == 0) return "Loading";
    if (s == "activity:watch_video") return "Watching a cinematic";
    if (s.rfind("activity:", 0) == 0) return "In the world";
    return "Playing";
}

void worker(std::string app_id) {
    using namespace std::chrono;
    const int64_t started = duration_cast<seconds>(system_clock::now().time_since_epoch()).count();
    Ipc ipc;
    std::string last;
    auto next_connect = steady_clock::now();
    for (;;) {
        std::this_thread::sleep_for(seconds(2));
        if (!ipc.connected()) {
            if (steady_clock::now() < next_connect) continue;
            if (!ipc.connect_any(app_id)) {
                next_connect = steady_clock::now() + seconds(15);
                continue;
            }
            last.clear();
        }
        std::string details = describe(game_state());
        std::string activity = "{\"details\":\"" + json_escape(details) +
                               "\",\"state\":\"Custom Native PC Dev Build 1.33\",\"timestamps\":{\"start\":" +
                               std::to_string(started) +
                               "},\"assets\":{\"large_image\":\"destiny\",\"large_text\":\"Destiny\"}}";
        if (activity == last) continue;
        if (ipc.set_activity(activity)) last = activity;
    }
}

}  // namespace

void discord_start() {
    const auto& s = settings();
    if (!s.discord || s.discord_app_id.empty()) return;
    std::thread(worker, s.discord_app_id).detach();
}

}  // namespace d1
