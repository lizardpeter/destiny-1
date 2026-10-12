//! Importer progress reporting.
//!
//! Importers call [`report`] at coarse phase boundaries of a long import; the
//! host (game, tools) installs a hook to show it, e.g. on a loading screen.
//! Without a hook, reporting is a no-op.

use std::sync::RwLock;

/// `(phase description, phases done, phase count)`.
pub type ProgressHook = fn(&str, u32, u32);

static HOOK: RwLock<Option<ProgressHook>> = RwLock::new(None);

/// Install (or clear) the process-wide progress hook.
pub fn set_hook(hook: Option<ProgressHook>) {
    *HOOK.write().unwrap_or_else(|poisoned| poisoned.into_inner()) = hook;
}

/// Report that `done` of `total` phases are complete and `phase` is next.
pub fn report(phase: &str, done: u32, total: u32) {
    let hook = *HOOK.read().unwrap_or_else(|poisoned| poisoned.into_inner());
    if let Some(hook) = hook {
        hook(phase, done, total);
    }
}
