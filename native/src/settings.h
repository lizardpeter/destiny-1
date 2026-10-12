// User settings: <data>/d1-native.cfg (created with defaults on first run), overridden by
// environment variables for quick experiments.
#pragma once
#include <string>

namespace d1 {

struct Settings {
    // window
    int window_width = 1280;
    int window_height = 720;
    bool fullscreen = false;
    // "on" (vsync, Fifo), "off" (Mailbox: no vsync wait, no tearing), "off-tearing" (Immediate)
    std::string vsync = "off";
    // frame-rate target for the game's own limiter; 0 = the game's default (30)
    int fps = 0;
    // Discord Rich Presence
    bool discord = true;
    std::string discord_app_id = "1559335126528426075";  // the "Destiny" Discord application
};

void load_settings(const std::string& data_root, const std::string& explicit_path);
const Settings& settings();
std::string settings_path();

}  // namespace d1
