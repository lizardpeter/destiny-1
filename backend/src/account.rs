//! The account the backend serves: its characters, kept in `<data dir>/account.json`.
//!
//! A character is stored as the bitstream of its creation request (0x1F5, type 0x80801860:
//! {race/gender/class, appearance, ...}), decoded again whenever its objects are built.

use serde::{Deserialize, Serialize};
use std::{collections::HashMap, path::PathBuf, sync::Mutex};
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
    path: Option<PathBuf>,
    account: Account,
}

static STORE: Mutex<Option<Store>> = Mutex::new(None);

pub fn init(dir: Option<PathBuf>) {
    let path = dir.map(|d| {
        let _ = std::fs::create_dir_all(&d);
        d.join("account.json")
    });
    let account = path
        .as_ref()
        .and_then(|p| std::fs::read(p).ok())
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or_default();
    let a: &Account = &account;
    info!("account: {} characters ({})", a.characters.len(),
          path.as_ref().map(|p| p.display().to_string()).unwrap_or("not saved".into()));
    *STORE.lock().unwrap() = Some(Store { path, account });
}

pub fn with<R>(f: impl FnOnce(&mut Account) -> R) -> R {
    let mut g = STORE.lock().unwrap();
    let s = g.get_or_insert_with(|| Store { path: None, account: Account::default() });
    let r = f(&mut s.account);
    if let Some(p) = &s.path {
        match serde_json::to_vec_pretty(&s.account) {
            Ok(b) => {
                if let Err(e) = std::fs::write(p, b) {
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
