// Discord Rich Presence over the local Discord IPC socket (no SDK needed).
#pragma once

namespace d1 {
// Starts the presence worker if enabled in the settings and an application id is set.
// Fail-open: without a running Discord client nothing happens.
void discord_start();
}  // namespace d1
