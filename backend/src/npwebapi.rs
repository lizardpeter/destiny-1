//! PSN web API stand-in (libSceNpWebApi requests, forwarded by d1-native's HLE as
//! `<METHOD> /npwebapi/<api group><path>`).
//!
//! Answered so far:
//! - sessionInvitation `POST /v1/sessions`: create a session -> `{"sessionId": ...}`
//!   The multipart body's parts (session-request JSON, session-image, session-data,
//!   changeable-session-data) are kept per session; with a data directory they are also
//!   written to `<data>/sessions/<id>/<part>` (research: what a joining player reads).
//! - sessionInvitation `GET /v1/sessions/<id>/sessionData` and `.../changeableSessionData`:
//!   the stored binary part; `GET /v1/sessions/<id>`: the session (request JSON + members);
//!   `POST`/`DELETE /v1/sessions/<id>/members`: join/leave; `GET /v1/users/<id>/sessions`:
//!   the sessions a player is in (what the system software reads to join a friend).
//!   The caller is the online id in the PSN access token (`Authorization: Bearer ...`).
//! - userProfile `PUT /v1/users/<id>/presence/gameData`: the player's presence game data
//!   (base64 of the fireteam session data), kept per player.
//! - userProfile `GET /v1/users/<id>/friendList`: every other player the backend knows, as an
//!   online friend in Destiny with their presence game data (how a player finds a fireteam to
//!   join).
//! - anything else: 200 with `{}` (logged, so new calls show up in backend.log)

use axum::{
    body::Bytes,
    extract::Path,
    http::{header, HeaderMap, Method, StatusCode},
    response::{IntoResponse, Response},
    Json,
};
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

/// The calling player, from the PSN access token libSceNpWebApi sends ("Bearer d1b-D1NATIVE-<id>").
fn caller(headers: &HeaderMap) -> String {
    headers
        .get("authorization")
        .and_then(|h| h.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .map(|t| t.trim_start_matches("d1b-").trim_start_matches("D1NATIVE-").to_string())
        .unwrap_or_default()
}

/// Session id -> {creator, members (online ids)}; online id -> sessions they are in.
#[derive(Default)]
struct Membership {
    members: HashMap<String, Vec<String>>,
}

fn membership() -> &'static Mutex<Membership> {
    static M: OnceLock<Mutex<Membership>> = OnceLock::new();
    M.get_or_init(Default::default)
}

/// Sessions an online id is a member of (newest first).
fn sessions_of(user: &str) -> Vec<String> {
    let m = membership().lock().unwrap();
    let mut v: Vec<String> = m.members.iter().filter(|(_, ms)| ms.iter().any(|u| u == user)).map(|(id, _)| id.clone()).collect();
    v.sort();
    v.reverse();
    v
}

fn session_part(id: &str, part: &str) -> Option<Vec<u8>> {
    sessions().lock().unwrap().get(id)?.get(part).cloned()
}

fn json_reply(status: StatusCode, v: Value) -> Response {
    (status, Json(v)).into_response()
}

pub async fn request(method: Method, Path((group, path)): Path<(String, String)>, headers: HeaderMap, body: Bytes)
    -> Response {
    let ctype = headers.get("content-type").and_then(|h| h.to_str().ok()).unwrap_or("");
    let me = caller(&headers);
    let text = String::from_utf8_lossy(&body);
    let preview: String = text.chars().take(600).collect();
    info!("npwebapi: {me}: {method} {group}/{path} ({} bytes, {ctype})\n{preview}", body.len());
    let path = format!("/{path}");
    fn session_path(p: &str) -> Option<Vec<&str>> {
        p.strip_prefix("/v1/sessions/").map(|r| r.split('/').collect())
    }
    match (group.as_str(), method.as_str(), path.as_str()) {
        ("sessionInvitation", "POST", "/v1/sessions") => {
            let n = NEXT_SESSION.fetch_add(1, Ordering::Relaxed);
            // PSN session id as the game parses it (0x2E9B10): hex groups 3-8-4-4-4-12.
            let id = format!("D1B-{n:08X}-0000-0000-0000-{n:012X}");
            info!("npwebapi: session {id} created by {me}");
            store(&id, multipart(ctype, &body));
            let mut m = membership().lock().unwrap();
            // a player is in one session at a time
            for ms in m.members.values_mut() {
                ms.retain(|u| u != &me);
            }
            m.members.insert(id.clone(), vec![me.clone()]);
            json_reply(StatusCode::OK, json!({ "sessionId": id }))
        }
        ("sessionInvitation", "GET", p) if p.starts_with("/v1/users/") && p.ends_with("/sessions") => {
            // the sessions a user is in (what the system software reads to join a friend)
            let user = p.trim_start_matches("/v1/users/").trim_end_matches("/sessions").to_string();
            let user = if user == "me" { me.clone() } else { user };
            let list: Vec<Value> = sessions_of(&user).into_iter().map(|id| json!({ "sessionId": id, "platform": "PS4" })).collect();
            let n = list.len();
            info!("npwebapi: sessions of {user}: {n}");
            json_reply(StatusCode::OK, json!({ "start": 0, "size": n, "totalResults": n, "sessions": list }))
        }
        ("sessionInvitation", m, p) if session_path(p).is_some() => {
            let parts = session_path(p).unwrap();
            let id = parts[0].to_string();
            match (m, parts.get(1).copied()) {
                ("GET", Some(part @ ("sessionData" | "changeableSessionData"))) => {
                    let name = if part == "sessionData" { "session-data" } else { "changeable-session-data" };
                    match session_part(&id, name) {
                        Some(d) => {
                            info!("npwebapi: session {id} {part}: {} bytes", d.len());
                            ([(header::CONTENT_TYPE, "application/octet-stream")], d).into_response()
                        }
                        None => json_reply(StatusCode::NOT_FOUND, json!({ "error": { "code": 2113794, "message": "Session not found" } })),
                    }
                }
                ("PUT", Some("changeableSessionData")) => {
                    store(&id, vec![("changeable-session-data".into(), body.to_vec())]);
                    json_reply(StatusCode::OK, json!({}))
                }
                ("PUT", None) => {
                    // session update (sessionMaxUser, sessionName, ...): merged into the request
                    let end = body.iter().rposition(|&b| b != 0 && !b.is_ascii_whitespace()).map_or(0, |i| i + 1);
                    let upd: Value = serde_json::from_slice(&body[..end]).unwrap_or_else(|_| json!({}));
                    let mut v: Value = session_part(&id, "session-request")
                        .and_then(|r| serde_json::from_slice(&r).ok())
                        .unwrap_or_else(|| json!({}));
                    if let (Some(o), Some(u)) = (v.as_object_mut(), upd.as_object()) {
                        for (k, x) in u {
                            o.insert(k.clone(), x.clone());
                        }
                    }
                    store(&id, vec![("session-request".into(), serde_json::to_vec(&v).unwrap_or_default())]);
                    json_reply(StatusCode::OK, json!({}))
                }
                ("POST", Some("members")) => {
                    let mut m = membership().lock().unwrap();
                    for ms in m.members.values_mut() {
                        ms.retain(|u| u != &me);
                    }
                    m.members.entry(id.clone()).or_default().push(me.clone());
                    info!("npwebapi: {me} joined session {id}");
                    json_reply(StatusCode::OK, json!({}))
                }
                ("DELETE", Some("members")) => {
                    let mut m = membership().lock().unwrap();
                    if let Some(ms) = m.members.get_mut(&id) {
                        ms.retain(|u| u != &me);
                    }
                    info!("npwebapi: {me} left session {id}");
                    json_reply(StatusCode::OK, json!({}))
                }
                ("GET", None) => {
                    let Some(req) = session_part(&id, "session-request") else {
                        return json_reply(StatusCode::NOT_FOUND, json!({ "error": { "code": 2113794, "message": "Session not found" } }));
                    };
                    let mut v: Value = serde_json::from_slice(&req).unwrap_or_else(|_| json!({}));
                    let members = membership().lock().unwrap().members.get(&id).cloned().unwrap_or_default();
                    let creator = members.first().cloned().unwrap_or_default();
                    v["sessionId"] = json!(id);
                    v["sessionCreator"] = json!(creator);
                    v["sessionCreateTimestamp"] = json!(1359691347652u64);
                    v["members"] = json!(members.iter().map(|u| json!({ "onlineId": u, "platform": "PS4" })).collect::<Vec<_>>());
                    json_reply(StatusCode::OK, v)
                }
                _ => json_reply(StatusCode::OK, json!({})),
            }
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
            json_reply(StatusCode::OK, json!({}))
        }
        ("userProfile", "GET", p) if p.starts_with("/v1/users/") && p.contains("/friendList") => {
            let user = p.trim_start_matches("/v1/users/").split('/').next().unwrap_or("").to_string();
            let v = friend_list(&user);
            info!("npwebapi: friend list for {user}: {}", v["totalResults"]);
            json_reply(StatusCode::OK, v)
        }
        _ => json_reply(StatusCode::OK, json!({})),
    }
}
