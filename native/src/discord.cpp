// Discord Rich Presence through Discord's local IPC socket (the protocol Discord's own
// RPC libraries use): connect to discord-ipc-N, send a handshake with the application id,
// then SET_ACTIVITY frames. Same design as Rust-test's presence worker: one background
// thread owns the connection, the game never blocks on it, and every failure is ignored
// (retry later). Linux/macOS only for now, like d1-native itself.
#include "discord.h"

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>

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

class Ipc {
public:
    ~Ipc() { close_fd(); }
    bool connected() const { return fd_ >= 0; }

    bool connect_any(const std::string& app_id) {
        std::string dirs[] = {
            getenv("XDG_RUNTIME_DIR") ? getenv("XDG_RUNTIME_DIR") : "",
            getenv("XDG_RUNTIME_DIR") ? std::string(getenv("XDG_RUNTIME_DIR")) + "/app/com.discordapp.Discord" : "",
            getenv("XDG_RUNTIME_DIR") ? std::string(getenv("XDG_RUNTIME_DIR")) + "/snap.discord" : "",
            getenv("TMPDIR") ? getenv("TMPDIR") : "",
            "/tmp",
        };
        for (auto& d : dirs) {
            if (d.empty()) continue;
            for (int i = 0; i < 10; ++i) {
                std::string path = d + "/discord-ipc-" + std::to_string(i);
                int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
                if (fd < 0) return false;
                sockaddr_un sa{};
                sa.sun_family = AF_UNIX;
                std::strncpy(sa.sun_path, path.c_str(), sizeof sa.sun_path - 1);
                if (::connect(fd, reinterpret_cast<sockaddr*>(&sa), sizeof sa) == 0) {
                    fd_ = fd;
                    timeval tv{2, 0};
                    setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
                    if (send(0, "{\"v\":1,\"client_id\":\"" + json_escape(app_id) + "\"}") && read_frame()) {
                        log("discord: connected (%s)", path.c_str());
                        return true;
                    }
                    close_fd();
                    continue;
                }
                ::close(fd);
            }
        }
        return false;
    }

    bool set_activity(const std::string& activity_json) {
        static uint64_t nonce = 0;
        std::string msg = "{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":" + std::to_string(getpid()) +
                          ",\"activity\":" + activity_json + "},\"nonce\":\"" + std::to_string(++nonce) + "\"}";
        if (!send(1, msg) || !read_frame()) {
            close_fd();
            return false;
        }
        return true;
    }

private:
    bool send(uint32_t op, const std::string& json) {
        if (fd_ < 0) return false;
        std::string frame(8, '\0');
        uint32_t len = uint32_t(json.size());
        std::memcpy(frame.data(), &op, 4);
        std::memcpy(frame.data() + 4, &len, 4);
        frame += json;
        for (size_t off = 0; off < frame.size();) {
            ssize_t n = ::send(fd_, frame.data() + off, frame.size() - off, MSG_NOSIGNAL);
            if (n <= 0) return false;
            off += size_t(n);
        }
        return true;
    }
    bool read_frame() {  // reply contents are not needed; just keep the stream in sync
        uint32_t hdr[2];
        if (recv(fd_, hdr, 8, MSG_WAITALL) != 8) return false;
        std::string body(hdr[1], '\0');
        return hdr[1] == 0 || recv(fd_, body.data(), hdr[1], MSG_WAITALL) == ssize_t(hdr[1]);
    }
    void close_fd() {
        if (fd_ >= 0) ::close(fd_);
        fd_ = -1;
    }
    int fd_ = -1;
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
                               "\",\"state\":\"PS4 01.33 on d1-native\",\"timestamps\":{\"start\":" +
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
