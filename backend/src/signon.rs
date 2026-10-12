//! Bungie sign-on service: `POST https://www*.signon.{deadorbit,gravityshavings}.net/SignOn`
//! (`c_signon_service_client`). Request and response are protobuf.
//!
//! Response schema (eboot table 0x1910CC0; handler 0x2AA420, success path 0x2AADA0):
//! ```text
//!  1  int     response type: 0 success, 1 denied, 2 queued, 3 server offline
//!  2  msg     success (schema 0x1910DF0):
//!       1,2,3 bytes[16]  (2 and 3 are kept as session keys)
//!       4     bytes[<=512] security token
//!       5     int64  token expiry (absolute, seconds) — or 11: relative seconds
//!       6     uint32 IPv4 of the next server (host order; stored big-endian)
//!       7     uint32 port of the next server
//!       9     msg {1,2,3 float}
//!  3  msg     denial (0x15BA200): reason, message[256], ...
//!  4  msg     client_config (0x15B67E0): 1 cookie int64, 2 social_matchmaking_id int32,
//!             3 bytes: engine configuration stream (decoded by callback 0x2AAD90 ->
//!             0x1DB190 -> 0x1033F80): u32 magic 0x123456, then {u32 id, value}... ending
//!             with id 0. Id 100 = content manifest URL, 101 = its expected GUID, 102 =
//!             URL suffix (strings: varint length + bytes).
//!  5  int64   silo id
//!  6  string  content build version
//!  8  int     flags (bits copied to sign-on state)
//! 10  msg     {1 repeated int32}
//! 12  int64   server clock (seconds) — client logs its clock offset
//! 13  string  server environment
//! 14  int32   external IPv4 for STUN
//! ```

use crate::{pb, Shared};
use axum::{body::Bytes, extract::State, http::HeaderMap};
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::info;

pub async fn sign_on(State(st): State<Shared>, headers: HeaderMap, body: Bytes) -> Vec<u8> {
    let host = headers.get("host").and_then(|h| h.to_str().ok()).unwrap_or("?");
    info!("signon: request via {host}, {} bytes\n{}", body.len(), pb::dump(&body, 2));
    let now = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
    let ip = u32::from(st.public_ip);
    let success = pb::Msg::new()
        .bytes(1, &[0x11; 16])
        .bytes(2, &[0x22; 16])
        .bytes(3, &[0x33; 16])
        .bytes(4, b"d1-backend-security-token")
        .int(5, (now + 86400) as i64)
        .uint(6, u64::from(ip))
        .uint(7, u64::from(st.bap_port));
    let resp = pb::Msg::new()
        .uint(1, 0)
        .msg(2, success)
        .msg(4, pb::Msg::new().int(1, 1).int(2, 0).bytes(3, &client_config(&st)))
        .uint(5, 1)
        .str(6, &st.content_version)
        .int(12, now as i64)
        .str(13, "d1-backend");
    let out = resp.into_bytes();
    info!("signon: success -> next server {}:{} ({} bytes)", st.public_ip, st.bap_port, out.len());
    out
}

/// Engine configuration ("client config") stream carried in sign-on field 4.3.
fn client_config(st: &Shared) -> Vec<u8> {
    let mut b = Vec::new();
    b.extend_from_slice(&0x123456u32.to_le_bytes());
    let mut string = |id: u32, s: &str| {
        b.extend_from_slice(&id.to_le_bytes());
        let mut n = s.len() as u64;
        loop {
            let c = (n & 0x7f) as u8;
            n >>= 7;
            b.push(if n == 0 { c } else { c | 0x80 });
            if n == 0 {
                break;
            }
        }
        b.extend_from_slice(s.as_bytes());
    };
    string(100, &st.manifest_url);
    string(101, crate::content::MANIFEST_GUID);
    b.extend_from_slice(&0u32.to_le_bytes());
    b
}
