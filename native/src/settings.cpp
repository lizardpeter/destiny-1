#include "settings.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>

#include "hle.h"

namespace d1 {

static Settings g_settings;
static std::string g_path;

const Settings& settings() { return g_settings; }
std::string settings_path() { return g_path; }

static const char* kDefaultFile = R"(# d1-native settings. Environment variables override these (shown in brackets).

# The installed game (CUSA00219 01.33: eboot.bin, sce_module, packages). Only ever read.
# A path relative to this folder, or a full path such as D:/Games/CUSA00219.
game_dir = game                # [D1_GAME_DIR]

# Backend: local (start d1-backend from this folder), off, or a server's host name / IP.
backend = local                # [D1_BACKEND]

# Window size in pixels and fullscreen (F11 or Alt+Enter toggles while running).
window_width = 1280            # [D1_WINDOW_SIZE=1920x1080]
window_height = 720
fullscreen = false             # [D1_FULLSCREEN=1]

# V-sync: on | off | off-tearing
#   on          wait for the display refresh (smoothest, adds latency)
#   off         present the newest frame without waiting, no tearing (default)
#   off-tearing present immediately (lowest latency, may tear)
vsync = off                    # [D1_VSYNC]

# Stats overlay (FPS, render/window resolution, v-sync, GPU). F3 toggles it while running.
overlay = false                # [D1_OVERLAY=1]

# Frame-rate target. 0 keeps the game's own 30 fps.
fps = 0                        # [D1_FPS]

# Discord Rich Presence (needs the Discord desktop app running).
discord = true                 # [D1_DISCORD=0]
discord_app_id = 1559335126528426075   # [D1_DISCORD_APP_ID]

# Research hooks that get the boot past sign-in checks the backend cannot answer yet.
bypass = prereq,transport      # [D1_BYPASS]
)";

static bool truthy(const std::string& v) { return v == "1" || v == "true" || v == "on" || v == "yes"; }

static void apply_setting(const std::string& key, const std::string& v) {
    auto& s = g_settings;
    if (key == "game_dir") s.game_dir = v;
    else if (key == "backend") s.backend = v;
    else if (key == "bypass") s.bypass = v;
    else if (key == "window_width") s.window_width = std::atoi(v.c_str());
    else if (key == "window_height") s.window_height = std::atoi(v.c_str());
    else if (key == "fullscreen") s.fullscreen = truthy(v);
    else if (key == "vsync") s.vsync = v;
    else if (key == "overlay") s.overlay = truthy(v);
    else if (key == "fps") s.fps = std::atoi(v.c_str());
    else if (key == "discord") s.discord = truthy(v);
    else if (key == "discord_app_id") s.discord_app_id = v;
    else log("settings: unknown key '%s'", key.c_str());
}

void load_settings(const std::string& path) {
    g_path = path;
    std::ifstream in(g_path);
    if (!in) {
        std::ofstream(g_path) << kDefaultFile;
        in.open(g_path);
    }
    std::string line;
    while (std::getline(in, line)) {
        if (auto h = line.find('#'); h != std::string::npos) line.resize(h);
        auto eq = line.find('=');
        if (eq == std::string::npos) continue;
        auto trim = [](std::string x) {
            x.erase(0, x.find_first_not_of(" \t\r"));
            x.erase(x.find_last_not_of(" \t\r") + 1);
            return x;
        };
        std::string k = trim(line.substr(0, eq)), v = trim(line.substr(eq + 1));
        if (!k.empty()) apply_setting(k, v);
    }
    auto& s = g_settings;
    if (const char* v = getenv("D1_GAME_DIR")) s.game_dir = v;
    if (const char* v = getenv("D1_BACKEND")) s.backend = v;
    if (const char* v = getenv("D1_BYPASS")) s.bypass = v;
    if (const char* v = getenv("D1_WINDOW_SIZE")) std::sscanf(v, "%dx%d", &s.window_width, &s.window_height);
    if (const char* v = getenv("D1_FULLSCREEN")) s.fullscreen = truthy(v);
    if (const char* v = getenv("D1_VSYNC")) s.vsync = v;
    if (const char* v = getenv("D1_FPS")) s.fps = std::atoi(v);
    if (const char* v = getenv("D1_OVERLAY")) s.overlay = truthy(v);
    if (const char* v = getenv("D1_DISCORD")) s.discord = truthy(v);
    if (const char* v = getenv("D1_DISCORD_APP_ID")) s.discord_app_id = v;
    log("settings: %s (game %s, backend %s, window %dx%d%s, vsync %s, fps %s, discord %s)", g_path.c_str(), s.game_dir.c_str(), s.backend.c_str(), s.window_width,
        s.window_height, s.fullscreen ? " fullscreen" : "", s.vsync.c_str(),
        s.fps ? std::to_string(s.fps).c_str() : "game default",
        !s.discord ? "off" : s.discord_app_id.empty() ? "no app id" : "on");
}

}  // namespace d1
