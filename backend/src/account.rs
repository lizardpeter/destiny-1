//! Player accounts the backend serves: characters and family versions per player.
//!
//! A player is named by their PSN online id, which reaches the backend through the PSN
//! authorization code (d1-native puts `D1NATIVE-<online id>` in it), the access token,
//! the sign-on security token and finally the BAP secure hello (`bap.rs`). Code running for
//! a BAP connection reads the player with [`current`]; everything else uses the first player.
//!
//! Players get a slot in order of first appearance (kept in `<data>/players.json`). Slot 0 is
//! the original single account: `<data>/account.json` and ids 0x4D31_0000_0000_0001 (account)
//! / 0x4D31_0000_0000_0100.. (characters). Slot n > 0 lives in `<data>/accounts/<name>.json`
//! with every id offset by n << 32.
//!
//! A character is stored as the bitstream of its creation request (0x1F5, type 0x80801860:
//! {race/gender/class, appearance, ...}), decoded again whenever its objects are built.

use serde::{Deserialize, Serialize};
use std::{cell::RefCell, collections::HashMap, path::PathBuf, sync::Mutex};
use tracing::{info, warn};

#[derive(Serialize, Deserialize, Clone)]
pub struct Character {
    pub id: i64,
    /// hex of the 0x1F5 request body (without the u16 message id and has_extra bit)
    pub creation: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct Account {
    pub characters: Vec<Character>,
    /// last version sent per family type (queuez versions must keep increasing)
    #[serde(default)]
    pub versions: HashMap<u32, i32>,
}

struct Store {
    dir: Option<PathBuf>,
    /// online id -> slot
    slots: Vec<String>,
    accounts: HashMap<usize, Account>,
}

static STORE: Mutex<Option<Store>> = Mutex::new(None);

tokio::task_local! {
    /// The player a BAP connection serves (set from its secure hello).
    pub static PLAYER: RefCell<Option<String>>;
}

/// Default online id when nothing names the player (the first slot's name, if any).
const DEFAULT_PLAYER: &str = "";

pub fn init(dir: Option<PathBuf>) {
    if let Some(d) = &dir {
        let _ = std::fs::create_dir_all(d.join("accounts"));
    }
    let slots: Vec<String> = dir
        .as_ref()
        .and_then(|d| std::fs::read(d.join("players.json")).ok())
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or_default();
    let mut s = Store { dir, slots, accounts: HashMap::new() };
    let a = load(&s, 0);
    info!("account: {} players known; first account {} characters", s.slots.len(), a.characters.len());
    s.accounts.insert(0, a);
    *STORE.lock().unwrap() = Some(s);
}

fn file(s: &Store, slot: usize) -> Option<PathBuf> {
    let d = s.dir.as_ref()?;
    Some(if slot == 0 { d.join("account.json") } else { d.join("accounts").join(format!("{}.json", s.slots[slot])) })
}

fn load(s: &Store, slot: usize) -> Account {
    file(s, slot)
        .and_then(|p| std::fs::read(p).ok())
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or_default()
}

/// The current player's online id ("" when unknown).
pub fn current() -> String {
    PLAYER.try_with(|p| p.borrow().clone()).ok().flatten().unwrap_or_else(|| DEFAULT_PLAYER.to_string())
}

/// Name the player of the current BAP connection.
pub fn set_current(name: &str) {
    let _ = PLAYER.try_with(|p| *p.borrow_mut() = Some(name.to_string()));
    let slot = slot_of(name);
    info!("account: connection is player {name:?} (slot {slot})");
}

/// Slot of a player (assigned on first use; "" is slot 0).
pub fn slot_of(name: &str) -> usize {
    let mut g = STORE.lock().unwrap();
    let s = g.get_or_insert_with(|| Store { dir: None, slots: Vec::new(), accounts: HashMap::new() });
    if name.is_empty() {
        return 0;
    }
    if let Some(i) = s.slots.iter().position(|n| n == name) {
        return i;
    }
    s.slots.push(name.to_string());
    let i = s.slots.len() - 1;
    if let Some(d) = &s.dir {
        let _ = std::fs::write(d.join("players.json"), serde_json::to_vec_pretty(&s.slots).unwrap_or_default());
    }
    info!("account: new player {name:?} -> slot {i}");
    i
}

/// Id offset of the current player's slot.
pub fn id_offset() -> i64 {
    (slot_of(&current()) as i64) << 32
}

pub fn with<R>(f: impl FnOnce(&mut Account) -> R) -> R {
    let slot = slot_of(&current());
    let mut g = STORE.lock().unwrap();
    let s = g.get_or_insert_with(|| Store { dir: None, slots: Vec::new(), accounts: HashMap::new() });
    if !s.accounts.contains_key(&slot) {
        let a = load(s, slot);
        s.accounts.insert(slot, a);
    }
    let r = f(s.accounts.get_mut(&slot).unwrap());
    if let Some(p) = file(s, slot) {
        match serde_json::to_vec_pretty(&s.accounts[&slot]) {
            Ok(b) => {
                if let Err(e) = std::fs::write(&p, b) {
                    warn!("account: cannot save {}: {e}", p.display());
                }
            }
            Err(e) => warn!("account: {e}"),
        }
    }
    r
}

pub fn characters() -> Vec<Character> {
    with(|a| a.characters.clone())
}

/// Next queuez version for a family (baselines start at 1).
pub fn next_version(family: u32) -> i32 {
    with(|a| {
        let v = a.versions.entry(family).or_insert(0);
        *v += 1;
        *v
    })
}
