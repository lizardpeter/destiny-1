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

/// Host -> client message: activity membership (type 11, 0x29D130), 0x5038 bytes:
/// ```text
/// @0 u32, @4 u32 (update id; a change resets the client's +0x64B4)
/// @8 players[20], 0x250 each: identity {machine[8], player[8], account, character,
///    fireteam} (optional), state (optional), @0x248 i8 slot index (optional)
/// @0x2E48 optional fireteam block
/// @0x5028 / @0x502C / @0x5030 optional u20 masks; @0x502C = valid player slots
/// ```
/// The client finds itself by machine id among the valid slots (0x2A5520) and then marks
/// itself established (+0x131 bit 0).
pub const HOST_MEMBERSHIP: u32 = 11;
const TYPE_MEMBERSHIP: &str = "0x808009ed";

/// Membership with the given players (identity blocks) in slots 0.., all valid.
pub fn membership(players: &[Value]) -> Vec<u8> {
    let slots: Vec<Option<Value>> = players
        .iter()
        .enumerate()
        .map(|(i, id)| Some(Value::Struct(vec![Some(id.clone()), None, Some(Value::Int(i as i64))])))
        .collect();
    let mask = (1i64 << players.len()) - 1;
    let v = Value::Struct(vec![
        Some(Value::Int(1)),
        Some(Value::Int(1)),
        Some(Value::Array(slots)),
        None,
        Some(Value::Int(mask)),
        Some(Value::Int(mask)),
        Some(Value::Int(0)),
    ]);
    let mut w = BitWriter::default();
    invest::encode(&mut w, TYPE_MEMBERSHIP, &v);
    w.finish()
}

/// Host -> client message: instance state (type 1, 0x1018990 -> instance +0x50B0 via
/// 0x2A2C60), 0x6B0 bytes (0x80800B8F): bool valid @0, bool @1, bool @2, i64 @8, i32 @0x10,
/// char[64] @0x14, i32 @0x54, u32 @0x58, u32 @0x5C, details @0x60. The activity manager
/// waits for "instantiation" (0x2998F0) until valid is set and @1 is clear.
pub const HOST_INSTANCE: u32 = 1;
/// Scenario to load for an activity index: the named tag (e.g. "act_cosmo_m0_highway") and
/// its checksum, the u32 at +0xC of that tag's data, which the client compares with the
/// instance's +0x5C after loading (0x299B00, "activity checksum mismatch"). Only the
/// new-character prologue is known so far; the activity definitions in content hold the rest.
/// `bubbles` is the bubble (zone) count at +0x48 of the tag data, which must match the
/// instance's +0x10 (0x2A0D20, "invalid host activity state").
pub struct Scenario {
    pub name: &'static str,
    pub checksum: u32,
    pub bubbles: u32,
}

pub fn scenario_for(activity_index: i32) -> Option<Scenario> {
    match activity_index {
        // prologue, activity 0x6E0DAE89
        164 => Some(Scenario { name: "act_cosmo_m0_highway", checksum: 0x8FE0_7299, bubbles: 22 }),
        _ => None,
    }
}
const TYPE_INSTANCE: &str = "0x80800e76";

/// Details (0x80800CC5 @0x60): ..., @0x628 char[40] activity (scenario) name: the named tag
/// the client loads (e.g. "act_cosmo_m0_highway"; looked up across package named tables by
/// 0xD8970). The prologue loader reads it through 0x29A5E0 / 0x75F040.
pub fn instance(activity_name: &str, checksum: u32, bubbles: u32, activity_index: i32, insertion_point: i32) -> Vec<u8> {
    let name: Vec<Option<Value>> = activity_name.bytes().take(39).map(|c| Some(Value::Int(c as i64))).collect();
    // @0x620 u16 activity index (read back by 0x78DF40), @0x622 u16 insertion point
    let mut details = vec![None; 10];
    details[7] = Some(Value::Int(activity_index as i64));
    details[8] = Some(Value::Int(insertion_point as i64));
    details.push(Some(Value::Struct(vec![Some(Value::Array(name))])));
    let mut fields = vec![Some(Value::Bool(true)), Some(Value::Bool(false)), Some(Value::Bool(false))];
    // @0x10 bubble count, @0x14 per-bubble state (-1 = default, 0x2A0D20)
    fields.push(Some(Value::Int(0))); // @8
    fields.push(Some(Value::Int(bubbles as i64)));
    fields.push(Some(Value::Array((0..bubbles).map(|_| Some(Value::Int(-1))).collect())));
    fields.resize(8, None);
    fields.push(Some(Value::Int(checksum as i64))); // @0x5C
    fields.push(Some(Value::Struct(details)));
    let state = Value::Struct(fields);
    let mut w = BitWriter::default();
    invest::encode(&mut w, TYPE_INSTANCE, &Value::Struct(vec![Some(state)]));
    w.finish()
}

/// Per-connection activity host state.
#[derive(Default)]
pub struct Host {
    logged: std::collections::HashSet<u32>,
    /// From the host startup request: activity index and insertion point.
    activity: Option<(i32, i32)>,
}

impl Host {
    /// Host startup request (activity host manager request kind 3), after the kind byte:
    /// a bitstream starting u32, u16 activity index (+0x8000), u16 insertion point (+0x8000).
    pub fn on_startup(&mut self, p: &[u8]) {
        if p.len() >= 8 {
            let index = u16::from_be_bytes([p[4], p[5]]) as i32 - 0x8000;
            let insertion = u16::from_be_bytes([p[6], p[7]]) as i32 - 0x8000;
            info!("activity host: startup for activity index {index}, insertion point {insertion}");
            self.activity = Some((index, insertion));
        }
    }

    /// Handle one client message; returns host messages to send back (type, data).
    pub fn on_client(&mut self, m: &ClientMessage) -> Vec<(u32, Vec<u8>)> {
        match m.ty {
            CLIENT_JOIN_REQUEST => {
                let identity = join_identity(m.data);
                info!("activity host: join request {}", invest::show(&identity));
                let player = match &identity {
                    Value::Struct(f) => f.get(2).cloned().flatten(),
                    _ => None,
                };
                vec![
                    (HOST_JOIN_RESULT, join_result(&identity)),
                    (HOST_ENTITY_INDICES, entity_indices()),
                    (HOST_MEMBERSHIP, membership(player.as_slice())),
                    (HOST_INSTANCE, self.instance()),
                ]
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

impl Host {
    fn instance(&self) -> Vec<u8> {
        let (index, insertion) = self.activity.unwrap_or((-1, -1));
        match scenario_for(index) {
            Some(sc) => instance(sc.name, sc.checksum, sc.bubbles, index, insertion),
            None => {
                warn!("activity host: no scenario known for activity index {index}");
                instance("", 0, 0, index, insertion)
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

#[cfg(test)]
mod instance_tests {
    use super::*;

    #[test]
    fn instance_name_roundtrip() {
        let bytes = instance("act_cosmo_m0_highway", 0x8FE0_7299, 22, 164, -1);
        let v = invest::decode(&mut BitReader::new(&bytes), TYPE_INSTANCE);
        let s = invest::show(&v);
        assert!(s.contains("\"act_cosmo_m0_highway\""), "{s}");
    }
}
