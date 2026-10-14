#include "settings.h"

#include <cctype>
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

# Your name in the game (PSN online id): 3-16 letters, digits, - or _.
name = Guardian                # [D1_NAME]

# Backend: local (start d1-backend from this folder), off, or a server's host name / IP.
backend = local                # [D1_BACKEND]

# Internal render resolution: the size the game itself renders at (1920x1080 on the
# console), e.g. 2560x1440 or 3840x2160. Not an upscale: every render target is this size.
render_resolution = 1920x1080  # [D1_RENDER_RESOLUTION=2560x1440]

# Window size in pixels and fullscreen (F11 or Alt+Enter toggles while running).
window_width = 1280            # [D1_WINDOW_SIZE=1920x1080]
window_height = 720
fullscreen = false             # [D1_FULLSCREEN=1]

# V-sync: on | off | off-tearing
#   on          wait for the display refresh (smoothest, adds latency)
#   off         present the newest frame at the next refresh, no tearing
#   off-tearing present immediately (lowest latency, may tear; default). With G-Sync /
#               FreeSync, cap fps a few frames under the refresh rate to avoid tearing.
vsync = off-tearing            # [D1_VSYNC]

# Stats overlay (FPS, render/window resolution, v-sync, GPU). F3 toggles it while running.
overlay = false                # [D1_OVERLAY=1]

# Frame-rate limit: 0 = unlimited (one game tick per rendered frame), or a cap such as
# 60, 120 or 144 (30 is the console's own rate). Use vsync = on to lock to the display.
fps = 0                        # [D1_FPS]

# Discord Rich Presence (needs the Discord desktop app running).
discord = true                 # [D1_DISCORD=0]
discord_app_id = 1559335126528426075   # [D1_DISCORD_APP_ID]

# Copy the game's own log messages into d1-native.log (useful when reporting problems).
game_log = true                # [D1_GAME_LOG]

# Mouse look (raw counts go straight into the game's aim, no stick emulation, no
# acceleration, no aim assist). Sensitivity uses the Destiny 2 PC scale (also Modern
# Warfare 2019 / Overwatch): 1.0 = 0.0066 degrees per count, so the same number feels the
# same as in Destiny 2. 1.5 at 3200 DPI is 28.9 cm per 360.
# Zoom scale: 1 = the game's own aim-down-sights slowdown, 0 = the same speed when zoomed.
sensitivity = 1.5              # [D1_SENSITIVITY]
mouse_invert = false           # [D1_MOUSE_INVERT=1]
mouse_zoom_scale = 1.0         # [D1_MOUSE_ZOOM_SCALE]

# Skip the intro cinematic that plays before the first mission.
skip_intro = true              # [D1_SKIP_INTRO=0]

# Research hooks for checks the backend cannot answer yet: prereq/transport (sign-in),
# localres (load global resources locally), spawn (finish loading into a mission once the
# player has spawned).
bypass = prereq,transport,localres,spawn   # [D1_BYPASS]
)";

static bool truthy(const std::string& v) { return v == "1" || v == "true" || v == "on" || v == "yes"; }

static void apply_setting(const std::string& key, const std::string& v) {
    auto& s = g_settings;
    if (key == "game_dir") s.game_dir = v;
    else if (key == "backend") s.backend = v;
    else if (key == "bypass") s.bypass = v;
    else if (key == "render_resolution") std::sscanf(v.c_str(), "%dx%d", &s.render_width, &s.render_height);
    else if (key == "window_width") s.window_width = std::atoi(v.c_str());
    else if (key == "window_height") s.window_height = std::atoi(v.c_str());
    else if (key == "fullscreen") s.fullscreen = truthy(v);
    else if (key == "vsync") s.vsync = v;
    else if (key == "overlay") s.overlay = truthy(v);
    else if (key == "fps") s.fps = (v == "unlimited" || v == "max") ? 0 : std::atoi(v.c_str());
    else if (key == "discord") s.discord = truthy(v);
    else if (key == "discord_app_id") s.discord_app_id = v;
    else if (key == "name") s.name = v;
    else if (key == "game_log") s.game_log = truthy(v);
    else if (key == "skip_intro") s.skip_intro = truthy(v);
    else if (key == "sensitivity") s.mouse_sensitivity = std::atof(v.c_str());
    else if (key == "mouse_sensitivity") {  // older configs: Source scale (0.022 degrees per count)
        s.mouse_sensitivity = std::atof(v.c_str()) * 0.022 / 0.0066;
        log("settings: mouse_sensitivity (Source scale) %s = sensitivity %.2f on the Destiny 2 scale; "
            "use 'sensitivity' instead", v.c_str(), s.mouse_sensitivity);
    }
    else if (key == "mouse_invert") s.mouse_invert = truthy(v);
    else if (key == "mouse_zoom_scale") s.mouse_zoom_scale = std::atof(v.c_str());
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
    if (const char* v = getenv("D1_RENDER_RESOLUTION")) std::sscanf(v, "%dx%d", &s.render_width, &s.render_height);
    if (s.render_width < 640 || s.render_height < 360 || s.render_width > 7680 || s.render_height > 4320) {
        log("settings: render_resolution %dx%d out of range; using 1920x1080", s.render_width, s.render_height);
        s.render_width = 1920, s.render_height = 1080;
    }
    if (const char* v = getenv("D1_WINDOW_SIZE")) std::sscanf(v, "%dx%d", &s.window_width, &s.window_height);
    if (const char* v = getenv("D1_FULLSCREEN")) s.fullscreen = truthy(v);
    if (const char* v = getenv("D1_VSYNC")) s.vsync = v;
    if (const char* v = getenv("D1_FPS")) s.fps = std::atoi(v);
    if (const char* v = getenv("D1_OVERLAY")) s.overlay = truthy(v);
    if (const char* v = getenv("D1_DISCORD")) s.discord = truthy(v);
    if (const char* v = getenv("D1_DISCORD_APP_ID")) s.discord_app_id = v;
    if (const char* v = getenv("D1_NAME")) s.name = v;
    if (const char* v = getenv("D1_SKIP_INTRO")) s.skip_intro = truthy(v);
    if (const char* v = getenv("D1_SENSITIVITY")) s.mouse_sensitivity = std::atof(v);
    if (const char* v = getenv("D1_MOUSE_INVERT")) s.mouse_invert = truthy(v);
    if (const char* v = getenv("D1_MOUSE_ZOOM_SCALE")) s.mouse_zoom_scale = std::atof(v);
    {
        bool ok = s.name.size() >= 3 && s.name.size() <= 16;
        for (char c : s.name) ok &= std::isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_';
        if (!ok) {
            log("settings: name '%s' is not a valid online id (3-16 of A-Z a-z 0-9 - _); using Guardian", s.name.c_str());
            s.name = "Guardian";
        }
    }
    log("settings: name %s", s.name.c_str());
    log("settings: render resolution %dx%d", s.render_width, s.render_height);
    log("settings: %s (game %s, backend %s, window %dx%d%s, vsync %s, fps %s, discord %s)", g_path.c_str(), s.game_dir.c_str(), s.backend.c_str(), s.window_width,
        s.window_height, s.fullscreen ? " fullscreen" : "", s.vsync.c_str(),
        s.fps ? std::to_string(s.fps).c_str() : "unlimited",
        !s.discord ? "off" : s.discord_app_id.empty() ? "no app id" : "on");
}

}  // namespace d1
