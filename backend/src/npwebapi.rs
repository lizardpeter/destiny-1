//! PSN web API stand-in (libSceNpWebApi requests, forwarded by d1-native's HLE as
//! `<METHOD> /npwebapi/<api group><path>`).
//!
//! Answered so far:
//! - sessionInvitation `POST /v1/sessions`: create a session -> `{"sessionId": ...}`
//!   The multipart body's parts (session-request JSON, session-image, session-data,
//!   changeable-session-data) are kept per session; with a data directory they are also
//!   written to `<data>/sessions/<id>/<part>` (research: what a joining player reads).
//! - sessionInvitation `GET /v1/sessions/<id>/sessionData` and `.../changeableSessionData`:
//!   the stored binary part.
//! - userProfile `PUT /v1/users/<id>/presence/gameData`: the player's presence game data
//!   (base64 of the fireteam session data), kept per player.
//! - userProfile `GET /v1/users/<id>/friendList`: every other player the backend knows, as an
//!   online friend in Destiny with their presence game data (how a player finds a fireteam to
//!   join).
//! - anything else: 200 with `{}` (logged, so new calls show up in backend.log)

use axum::{body::Bytes, extract::Path, http::{HeaderMap, Method, StatusCode}, Json};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Mutex, OnceLock};
use tracing::{info, warn};

static NEXT_SESSION: AtomicU64 = AtomicU64::new(1);

/// Session id -> multipart parts by Content-Description.
fn sessions() -> &'static Mutex<HashMap<String, HashMap<String, Vec<u8>>>> {
    static S: OnceLock<Mutex<HashMap<String, HashMap<String, Vec<u8>>>>> = OnceLock::new();
    S.get_or_init(Default::default)
}

static DATA_DIR: OnceLock<Option<std::path::PathBuf>> = OnceLock::new();

/// Online id -> presence game data (base64 string as the game sent it).
fn presence() -> &'static Mutex<HashMap<String, String>> {
    static P: OnceLock<Mutex<HashMap<String, String>>> = OnceLock::new();
    P.get_or_init(Default::default)
}

/// A player's fireteam session data (78 bytes: host address, id, security key), from the
/// presence game data they published.
pub fn session_data(name: &str) -> Option<Vec<u8>> {
    use base64::Engine;
    let p = presence().lock().unwrap();
    base64::engine::general_purpose::STANDARD.decode(p.get(name)?).ok()
}

fn friend_list(me: &str) -> Value {
    let p = presence().lock().unwrap();
    let mut names = crate::account::players();
    for id in p.keys() {
        if !names.contains(id) {
            names.push(id.clone());
        }
    }
    let empty = String::new();
    let friends: Vec<Value> = names
        .iter()
        .filter(|id| id.as_str() != me)
        .map(|id| (id, p.get(id).unwrap_or(&empty)))
        .map(|(id, game_data)| {
            json!({
                "onlineId": id,
                "npId": format!("{id}@d1.us"),
                "region": "us",
                "avatarUrl": "",
                "presence": { "primaryInfo": {
                    "onlineStatus": "online",
                    "platformInfoList": [{ "platform": "PS4", "onlineStatus": "online" }],
                    "gameTitleInfo": { "npTitleId": "CUSA00219_00", "titleName": "Destiny" },
                    "gameStatus": "",
                    "gameData": game_data,
                }},
            })
        })
        .collect();
    let n = friends.len();
    json!({ "friendList": friends, "start": 0, "size": n, "totalResults": n })
}
pub fn init(data_dir: Option<std::path::PathBuf>) {
    let _ = DATA_DIR.set(data_dir);
}

/// Split a multipart/mixed body into (Content-Description or Content-Type, data) parts.
fn multipart(ctype: &str, body: &[u8]) -> Vec<(String, Vec<u8>)> {
    let Some(b) = ctype.split("boundary=").nth(1) else { return Vec::new() };
    let delim = format!("--{}", b.trim_matches('"'));
    let d = delim.as_bytes();
    let mut out = Vec::new();
    let mut starts = Vec::new();
    let mut i = 0;
    while i + d.len() <= body.len() {
        if &body[i..i + d.len()] == d {
            starts.push(i);
            i += d.len();
        } else {
            i += 1;
        }
    }
    for w in starts.windows(2) {
        let part = &body[w[0] + d.len()..w[1]];
        let Some(h) = part.windows(4).position(|x| x == b"\r\n\r\n") else { continue };
        let head = String::from_utf8_lossy(&part[..h]).to_string();
        let mut data = part[h + 4..].to_vec();
        if data.ends_with(b"\r\n") {
            data.truncate(data.len() - 2);
        }
        let name = head
            .lines()
            .find_map(|l| l.strip_prefix("Content-Description:").map(|v| v.trim().to_string()))
            .or_else(|| head.lines().find_map(|l| l.strip_prefix("Content-Type:").map(|v| v.trim().to_string())))
            .unwrap_or_else(|| "part".into());
        out.push((name, data));
    }
    out
}

fn store(id: &str, parts: Vec<(String, Vec<u8>)>) {
    if let Some(Some(dir)) = DATA_DIR.get() {
        let d = dir.join("sessions").join(id);
        let _ = std::fs::create_dir_all(&d);
        for (name, data) in &parts {
            let _ = std::fs::write(d.join(name.replace('/', "_")), data);
        }
    }
    let mut s = sessions().lock().unwrap();
    let e = s.entry(id.to_string()).or_default();
    for (name, data) in parts {
        info!("npwebapi: session {id} part {name} ({} bytes)", data.len());
        e.insert(name, data);
    }
}

pub async fn request(method: Method, Path((group, path)): Path<(String, String)>, headers: HeaderMap, body: Bytes)
    -> (StatusCode, Json<Value>) {
    let ctype = headers.get("content-type").and_then(|h| h.to_str().ok()).unwrap_or("");
    let text = String::from_utf8_lossy(&body);
    let preview: String = text.chars().take(600).collect();
    info!("npwebapi: {method} {group}/{path} ({} bytes, {ctype})\n{preview}", body.len());
    let path = format!("/{path}");
    match (group.as_str(), method.as_str(), path.as_str()) {
        ("sessionInvitation", "POST", "/v1/sessions") => {
            let n = NEXT_SESSION.fetch_add(1, Ordering::Relaxed);
            let id = format!("00000000-0000-0000-0000-{n:012X}");
            info!("npwebapi: session {id} created");
            store(&id, multipart(ctype, &body));
            (StatusCode::OK, Json(json!({ "sessionId": id })))
        }
        ("sessionInvitation", "PUT", p) if p.starts_with("/v1/sessions/") && p.ends_with("/changeableSessionData") => {
            let id = p.trim_start_matches("/v1/sessions/").trim_end_matches("/changeableSessionData").to_string();
            store(&id, vec![("changeable-session-data".into(), body.to_vec())]);
            (StatusCode::OK, Json(json!({})))
        }
        ("userProfile", "PUT", p) if p.starts_with("/v1/users/") && p.ends_with("/presence/gameData") => {
            let user = p.trim_start_matches("/v1/users/").trim_end_matches("/presence/gameData").to_string();
            // The game sends the JSON padded with NULs/whitespace to its buffer size.
            let end = body.iter().rposition(|&b| b != 0 && !b.is_ascii_whitespace()).map_or(0, |i| i + 1);
            match serde_json::from_slice::<Value>(&body[..end]).ok().and_then(|v| v["gameData"].as_str().map(str::to_string)) {
                Some(gd) => {
                    info!("npwebapi: presence game data for {user} ({} chars)", gd.len());
                    presence().lock().unwrap().insert(user, gd);
                }
                None => warn!("npwebapi: unparsable presence game data for {user}"),
            }
            (StatusCode::OK, Json(json!({})))
        }
        ("userProfile", "GET", p) if p.starts_with("/v1/users/") && p.contains("/friendList") => {
            let user = p.trim_start_matches("/v1/users/").split('/').next().unwrap_or("").to_string();
            let v = friend_list(&user);
            info!("npwebapi: friend list for {user}: {}", v["totalResults"]);
            (StatusCode::OK, Json(v))
        }
        _ => (StatusCode::OK, Json(json!({}))),
    }
}
