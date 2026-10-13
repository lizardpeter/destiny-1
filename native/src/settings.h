// User settings: d1-native.cfg next to the executable (created with defaults on first run),
// overridden by environment variables for quick experiments.
#pragma once
#include <string>

namespace d1 {

struct Settings {
    // game files: the installed 01.33 game (eboot.bin, sce_module/, packages/), only ever
    // read. Relative paths are relative to the executable's folder.
    std::string game_dir = "game";
    // backend: "local" starts d1-backend from the executable's folder; "off" plays without
    // one; anything else is the host name or address of a backend server.
    std::string backend = "local";
    // research hooks needed to get past sign-in for now (see README)
    std::string bypass = "prereq,transport";
    // window
    int window_width = 1280;
    int window_height = 720;
    bool fullscreen = false;
    // "on" (vsync, Fifo), "off" (Mailbox: no vsync wait, no tearing), "off-tearing" (Immediate)
    std::string vsync = "off";
    // stats overlay (FPS, resolutions, v-sync, GPU) shown at start; F3 toggles it in game
    bool overlay = false;
    // frame-rate target for the game's own limiter; 0 = the game's default (30)
    int fps = 0;
    // Discord Rich Presence
    bool discord = true;
    std::string discord_app_id = "1559335126528426075";  // the "Destiny" Discord application
};

void load_settings(const std::string& path);
const Settings& settings();
std::string settings_path();

}  // namespace d1
