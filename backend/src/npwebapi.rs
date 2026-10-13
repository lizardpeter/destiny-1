//! PSN web API stand-in (libSceNpWebApi requests, forwarded by d1-native's HLE as
//! `<METHOD> /npwebapi/<api group><path>`).
//!
//! Answered so far:
//! - sessionInvitation `POST /v1/sessions`: create a session -> `{"sessionId": ...}`
//! - anything else: 200 with `{}` (logged, so new calls show up in backend.log)

use axum::{body::Bytes, extract::Path, http::{HeaderMap, Method, StatusCode}, Json};
use serde_json::{json, Value};
use std::sync::atomic::{AtomicU64, Ordering};
use tracing::info;

static NEXT_SESSION: AtomicU64 = AtomicU64::new(1);

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
            (StatusCode::OK, Json(json!({ "sessionId": id })))
        }
        _ => (StatusCode::OK, Json(json!({}))),
    }
}
