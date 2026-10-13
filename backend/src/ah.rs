//! Activity host (AH): the server that runs an activity instance (a mission, patrol, the
//! tower). The client finds it through BAP 16 (activity host proxy) and opens a second BAP
//! connection to it; after host startup (6 -> 7) the two exchange activity messages.
//!
//! Client -> host: notification 8 (header class 3: base header + u64 BE target AH id),
//! payload built by 0x55FD50:
//! ```text
//! u8 1 | u32 BE message type | u32 BE length | u32 BE (0) | data[length]
//! ```
//! Host -> client: bap_to_client_notification 9 (base header only; push policy 0x565440),
//! payload decoded by 0x55F2C0 (the same codec as activity_host_to_client 100, which the
//! client only relays to the service its header names):
//! ```text
//! u8 1 | u64 BE host id | u32 BE message type | u32 BE length (<= 0x1DF00) | data[length]
//! ```
//! `data` is an engine-type bitstream (decoder 0x2A4AC0), the same encoding as investment
//! messages. The client dispatches host messages through the table at 0x1910480
//! (type -> handler, payload type).

use crate::invest::{self, BitReader, BitWriter, Value};
use tracing::{info, warn};

/// Client -> host message: join request (type 3). Starts with the identity block.
pub const CLIENT_JOIN_REQUEST: u32 = 3;
/// Host -> client message: join result (type 4, handler 0x1018E30 / 0x29C710).
pub const HOST_JOIN_RESULT: u32 = 4;

/// Identity block shared by join request and result (0x100 bytes): i32 nonce, u64 host id,
/// {machine[8], player[8], account, character, fireteam}, optional properties, ...
const TYPE_IDENTITY: &str = "0x80800e98";
/// Join result (0x1A8 bytes): identity, u8 result (0 = joined) @0x100, session id string
/// @0x101, then counters; the client keeps the u16 @0x196 / @0x198.
const TYPE_JOIN_RESULT: &str = "0x80800a58";

pub struct ClientMessage<'a> {
    pub ty: u32,
    pub data: &'a [u8],
}

/// Parse a client -> host notification payload (after the 14-byte header class 3, whose
/// target id is the first 8 bytes of `payload` here).
pub fn parse_client(payload: &[u8]) -> Option<ClientMessage<'_>> {
    let p = payload.get(8..)?;
    if *p.first()? != 1 || p.len() < 13 {
        return None;
    }
    let ty = u32::from_be_bytes(p[1..5].try_into().ok()?);
    let len = u32::from_be_bytes(p[5..9].try_into().ok()?) as usize;
    let data = p.get(13..13 + len)?;
    Some(ClientMessage { ty, data })
}

/// Host -> client notification payload (see module docs).
pub fn host_payload(host_id: u64, ty: u32, data: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(17 + data.len());
    out.push(1);
    out.extend_from_slice(&host_id.to_be_bytes());
    out.extend_from_slice(&ty.to_be_bytes());
    out.extend_from_slice(&(data.len() as u32).to_be_bytes());
    out.extend_from_slice(data);
    out
}

/// Host -> client message: entity indices granted to the client (type 0, handler 0x1018800):
/// 384 u32 words, a bitmask OR-ed into the client's set (+0x5EA8); sets the "have entity
/// indices" flag (+0x64AA) the activity manager waits for after joining.
pub const HOST_ENTITY_INDICES: u32 = 0;
const TYPE_ENTITY_INDICES: &str = "0x80800d64";
const ENTITY_INDEX_WORDS: usize = 384;
/// Words of the entity index space granted to the client (indices 8192..12287); the rest
/// stay with the host.
const CLIENT_INDEX_WORDS: std::ops::Range<usize> = 256..384;

/// Per-connection activity host state.
#[derive(Default)]
pub struct Host {
    logged: std::collections::HashSet<u32>,
}

impl Host {
    /// Handle one client message; returns host messages to send back (type, data).
    pub fn on_client(&mut self, m: &ClientMessage) -> Vec<(u32, Vec<u8>)> {
        match m.ty {
            CLIENT_JOIN_REQUEST => {
                let identity = join_identity(m.data);
                info!("activity host: join request {}", invest::show(&identity));
                vec![(HOST_JOIN_RESULT, join_result(&identity)), (HOST_ENTITY_INDICES, entity_indices())]
            }
            t => {
                // Periodic messages (e.g. 15) are logged once.
                if self.logged.insert(t) || m.data.len() > 1 {
                    warn!("activity host: client message type {t} ({} bytes, unhandled): {}", m.data.len(),
                          crate::pb::hex(&m.data[..m.data.len().min(256)]));
                }
                Vec::new()
            }
        }
    }
}

pub fn entity_indices() -> Vec<u8> {
    let words = (0..ENTITY_INDEX_WORDS)
        .map(|i| Some(Value::Int(if CLIENT_INDEX_WORDS.contains(&i) { 0xFFFF_FFFF } else { 0 })))
        .collect();
    let mut w = BitWriter::default();
    invest::encode(&mut w, TYPE_ENTITY_INDICES, &Value::Struct(vec![Some(Value::Array(words))]));
    w.finish()
}

/// The identity block at the start of a join request.
pub fn join_identity(data: &[u8]) -> Value {
    invest::decode(&mut BitReader::new(data), TYPE_IDENTITY)
}

/// Join result accepting the request: identity echoed (nonce must match), result 0.
pub fn join_result(identity: &Value) -> Vec<u8> {
    let v = Value::Struct(vec![Some(identity.clone()), Some(Value::Int(0))]);
    let mut w = BitWriter::default();
    invest::encode(&mut w, TYPE_JOIN_RESULT, &v);
    w.finish()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn join_roundtrip() {
        let id = Value::Struct(vec![Some(Value::Int(649274874)), Some(Value::Int(0x4D31_4148_0000_0001))]);
        let bytes = join_result(&id);
        let back = invest::decode(&mut BitReader::new(&bytes), TYPE_JOIN_RESULT);
        let Value::Struct(f) = back else { panic!() };
        let Some(Value::Struct(ident)) = &f[0] else { panic!() };
        assert_eq!(ident[0], Some(Value::Int(649274874)));
        assert_eq!(ident[1], Some(Value::Int(0x4D31_4148_0000_0001)));
        assert_eq!(f[1], Some(Value::Int(0)));
        assert_eq!(&bytes[..4], &649274874u32.to_be_bytes());
    }
}
