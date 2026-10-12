//! PlayStation Network stand-in: just enough of the OAuth token endpoint for the game's
//! DemonWare PS4 authentication (`bdAuthPS4::handleGetAccessTokenReply`, eboot+0x122C070).
//!
//! The game posts `grant_type=authorization_code` with the code from
//! `sceNpAuthGetAuthorizationCode` and scope `openid,openid:duid,psn:s2s`. It parses the
//! JSON reply, requires `scope` and `id_token`, and forwards `{"scope","id_token"}` to the
//! DemonWare auth step. The token contents are ours to define; the matching backend
//! service is the only thing that reads them.

use axum::{body::Bytes, http::HeaderMap, Json};
use base64::Engine;
use serde_json::{json, Value};
use tracing::info;

pub async fn oauth_token(headers: HeaderMap, body: Bytes) -> Json<Value> {
    let form = String::from_utf8_lossy(&body);
    let field = |k: &str| {
        form.split('&')
            .find_map(|kv| kv.strip_prefix(&format!("{k}=")))
            .unwrap_or("")
            .to_string()
    };
    let code = field("code");
    let scope = field("scope").replace("%2C", ",").replace("%3A", ":");
    info!(
        "psn: oauth token for code {:?} (host {:?})",
        code,
        headers.get("host").and_then(|h| h.to_str().ok()).unwrap_or("?")
    );
    // A JWT-shaped id_token ("header.payload.signature"); nothing verifies the signature.
    let b64 = base64::engine::general_purpose::URL_SAFE_NO_PAD;
    let header = b64.encode(br#"{"alg":"none","typ":"JWT"}"#);
    let payload = b64.encode(
        json!({ "iss": "d1-backend", "sub": "d1native-user", "online_id": "D1NativeGuardian", "duid": "d1native" })
            .to_string(),
    );
    Json(json!({
        "access_token": format!("d1b-{code}"),
        "token_type": "bearer",
        "expires_in": 3600,
        "scope": scope,
        "id_token": format!("{header}.{payload}.d1b"),
    }))
}
