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
/// itself established (+0x131 bit 0). The membership also carries the host-tabulated region
/// table (@0x2E48) the slice-set manager needs before switching into a region.
pub const HOST_MEMBERSHIP: u32 = 11;
const TYPE_MEMBERSHIP: &str = "0x808009ed";

/// Host-tabulated region table (membership @0x2E48, 0x80800BD7): 40 entries of 0xD8
/// (0x80800C6F), a -1 id ends the list (0x778D60):
/// ```text
/// @0 i32 region (slice-set slot: bubble * 8 + set), @4 i2, @8 {i8, i2 @9 ambassador state,
/// i5 @0xA ambassador slot, bool @0x19 matchmaking threshold reached},
/// @0x20 u20, @0x28 {i8, u20, @0x38 i8[20] per-player transition token, string, i64}
/// ```
/// A region is ready for a player once its entry carries the player's current slice-set
/// transition token (1 for the initial transition) in that player's byte.
fn region_table(regions: &[i64], players: usize) -> Value {
    use Value::*;
    let tokens: Vec<Option<Value>> = (0..players).map(|_| Some(Int(1))).collect();
    let mut entries: Vec<Option<Value>> = regions
        .iter()
        .map(|&id| {
            Some(Struct(vec![
                Some(Int(id)),
                Some(Int(0)),
                // {u8, i2 ambassador state (1 assigned), i5 ambassador peer slot, bool @0x19
                // "a player reached the matchmaking threshold": the ambassador stops searching
                // for other public sessions and spins up a new one (0x77C3D0, +0x4A9)}. Nobody
                // else is in the region, so there is nothing to find.
                Some(Struct(vec![Some(Int(0)), Some(Int(1)), Some(Int(0)), Some(Bool(true))])),
                Some(Int(0)),
                Some(Struct(vec![Some(Int(0)), Some(Int(0)), Some(Array(tokens.clone()))])),
            ]))
        })
        .collect();
    while entries.len() < 40 {
        entries.push(Some(Struct(vec![Some(Int(-1))])));
    }
    Struct(vec![Some(Array(entries))])
}

/// Membership with the given players (identity blocks) in slots 0.., all valid.
/// A player in the activity, as given in its join request (0x80800E98 members 2 and 3).
#[derive(Clone)]
pub struct Player {
    /// {machine[8], player[8], account, character, fireteam} (0x80800C2D)
    pub identity: Value,
    /// {i8, session id, i64, i64, i64, fireteam id @0xA0, i32, i32, machine[8]} (0x80800B1F);
    /// the world controller finds a player's fireteam here (0x75F210)
    pub properties: Option<Value>,
}

pub fn membership(players: &[Player]) -> Vec<u8> {
    let slots: Vec<Option<Value>> = players
        .iter()
        .enumerate()
        .map(|(i, p)| {
            // slot state 0x80800C56: {properties, ?, ?, ?} (all optional)
            let state = p.properties.clone().map(|pr| Value::Struct(vec![Some(pr)]));
            Some(Value::Struct(vec![Some(p.identity.clone()), state, Some(Value::Int(i as i64))]))
        })
        .collect();
    let mask = (1i64 << players.len()) - 1;
    let v = Value::Struct(vec![
        Some(Value::Int(1)),
        Some(Value::Int(1)),
        Some(Value::Array(slots)),
        Some(region_table(&[0], players.len())),
        Some(Value::Int(mask)),
        Some(Value::Int(mask)),
        Some(Value::Int(0)),
    ]);
    // Decoded as an update of the client's current membership (0x2C9AE0): one "present"
    // bit, then the usual engine-type encoding (0x101EB30).
    let mut w = BitWriter::default();
    w.bit(true);
    invest::encode(&mut w, TYPE_MEMBERSHIP, &v);
    w.finish()
}

/// Host -> client message: instance state (type 1, 0x1018990 -> instance +0x50B0 via
/// 0x2A2C60), 0x6B0 bytes (0x80800B8F): bool valid @0, bool @1, bool @2, i64 @8, i32 @0x10,
/// char[64] @0x14, i32 @0x54, u32 @0x58, u32 @0x5C, details @0x60. The activity manager
/// waits for "instantiation" (0x2998F0) until valid is set and @1 is clear.
pub const HOST_INSTANCE: u32 = 1;

/// Host -> client message: world globals state (type 2, handler 0x1018D00, payload 0x80800DC1
/// = 0x80800D68 {bool valid, f32 value}), passed to the world interface (0x2409E0).
/// D1B_WORLD_GLOBAL=<f32> (research) sends it; the value is thought to be the time of day
/// (c_time_of_day_game_system starts at 0.2 with a 3600 s cycle).
pub const HOST_WORLD_GLOBALS: u32 = 2;

/// Host -> client message: claim authority over abandoned entity slots (type 23, handler
/// 0x10190F0 -> world interface slot 0x340; payload 0x80800D58 {u8, u32[384] slot mask, i3}).
/// D1B_CLAIM=<u8>,<i8> (research): hand the client the host's whole slot range (0..8191).
pub const HOST_CLAIM_ABANDONED: u32 = 23;

fn claim_abandoned() -> Option<(u32, Vec<u8>)> {
    let spec = std::env::var("D1B_CLAIM").ok()?;
    let mut it = spec.split(',').map(|x| x.trim().parse::<i64>().unwrap_or(0));
    let (a, b) = (it.next().unwrap_or(0), it.next().unwrap_or(-1));
    let words = (0..ENTITY_INDEX_WORDS).map(|i| Some(Value::Int(if CLIENT_INDEX_WORDS.contains(&i) { 0 } else { 0xFFFF_FFFF }))).collect();
    let mut w = BitWriter::default();
    invest::encode(&mut w, "0x80800d58", &Value::Struct(vec![Some(Value::Int(a)), Some(Value::Array(words)), Some(Value::Int(b))]));
    info!("activity host: claim abandoned entity slots 0..8191 ({a}, {b}) (D1B_CLAIM)");
    Some((HOST_CLAIM_ABANDONED, w.finish()))
}

fn world_globals() -> Option<(u32, Vec<u8>)> {
    let v: f32 = std::env::var("D1B_WORLD_GLOBAL").ok()?.parse().ok()?;
    let mut w = BitWriter::default();
    invest::encode(&mut w, "0x80800dc1", &Value::Struct(vec![Some(Value::Struct(vec![Some(Value::Bool(true)), Some(Value::Float(v))]))]));
    info!("activity host: world globals state {{true, {v}}} (D1B_WORLD_GLOBAL)");
    Some((HOST_WORLD_GLOBALS, w.finish()))
}
/// Scenario to load for an activity index: the scenario name (the activity's named tag, e.g.
/// "act_cosmo_m0_highway"), its checksum (u32 at +0xC of the `:scenario_client` tag, which the
/// client compares with the instance's +0x5C after loading: 0x299B00, "activity checksum
/// mismatch") and its bubble (zone) count (+0x48 of that tag, which must match the instance's
/// +0x10: 0x2A0D20, "invalid host activity state").
///
/// From `data/activities.json` (tools/d1_activity_table.py): every activity definition of the
/// client (index = the client's activity index, as in the host startup request) with the
/// scenario data read from the packages.
pub struct Scenario {
    pub name: String,
    pub checksum: u32,
    pub bubbles: u32,
}

#[derive(serde::Deserialize)]
struct ActivityRow {
    index: i32,
    hash: String,
    name: Option<String>,
    checksum: Option<String>,
    bubbles: Option<u32>,
}

fn activity_table() -> &'static std::collections::HashMap<i32, ActivityRow> {
    static T: std::sync::OnceLock<std::collections::HashMap<i32, ActivityRow>> = std::sync::OnceLock::new();
    T.get_or_init(|| {
        let rows: Vec<ActivityRow> = serde_json::from_str(include_str!("../data/activities.json")).expect("activities.json");
        rows.into_iter().map(|r| (r.index, r)).collect()
    })
}

fn hex_u32(s: &str) -> Option<u32> {
    u32::from_str_radix(s.trim_start_matches("0x"), 16).ok()
}

pub fn scenario_for(activity_index: i32) -> Option<Scenario> {
    let r = activity_table().get(&activity_index)?;
    Some(Scenario { name: r.name.clone()?, checksum: hex_u32(r.checksum.as_deref()?)?, bubbles: r.bubbles? })
}

/// Activity hash of an activity index (the client's matchmaking key).
pub fn activity_hash(activity_index: i32) -> Option<u32> {
    hex_u32(&activity_table().get(&activity_index)?.hash)
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
    // @0x10 bubble count, @0x14 per-bubble state: index of the slice set to load in that
    // bubble (0 = its first; -1 = none, leaving the bubble slot empty; 0x2A0D20)
    fields.push(Some(Value::Int(0))); // @8
    fields.push(Some(Value::Int(bubbles as i64)));
    fields.push(Some(Value::Array((0..bubbles).map(|_| Some(Value::Int(0))).collect())));
    fields.resize(8, None);
    fields.push(Some(Value::Int(checksum as i64))); // @0x5C
    fields.push(Some(Value::Struct(details)));
    let state = Value::Struct(fields);
    let mut w = BitWriter::default();
    invest::encode(&mut w, TYPE_INSTANCE, &Value::Struct(vec![Some(state)]));
    w.finish()
}

/// Host -> client message: sync token (type 27, 0x10193E0, payload 0x80800D31 {i32}); the
/// client stores it (+0x64AC) and echoes it in its type 28. Sent periodically as the host's
/// keep-alive: the client drops the host after 20 s without receiving anything (0x75FB20,
/// connection +0x1EF8 last-received time).
pub const HOST_SYNC_TOKEN: u32 = 27;
const TYPE_SYNC_TOKEN: &str = "0x80800d31";
pub const KEEPALIVE_INTERVAL: std::time::Duration = std::time::Duration::from_secs(5);

/// Host -> client message: client reference message (type 7, 0x29D7E0). Payload
/// (0x2D2B20): reference id 0x808004B1 {u32 group key, i8 (not -1), i16 index in the group},
/// payload type (0x80800046, a type handle), then a value of that type. The client looks the
/// reference up in the client reference manager (0x1071D0) and hands the value to the
/// object's message delegate at entry +0x108 (0x353340). The player (type 0xC) and activity
/// lifetime (type 0x10) references have no delegate there, so their state does not come
/// this way (findings/LOG.md, 2026-10-14 spawn).
#[allow(dead_code)]
pub const HOST_CLIENT_REFERENCE: u32 = 7;

/// Per-connection activity host state.
#[derive(Default)]
pub struct Host {
    logged: std::collections::HashSet<u32>,
    /// From the host startup request: activity index and insertion point.
    activity: Option<(i32, i32)>,
    joined: bool,
    sync_token: i64,
}

impl Host {
    /// Periodic host message once the client has joined.
    pub fn keepalive(&mut self) -> Vec<(u32, Vec<u8>)> {
        if !self.joined {
            return Vec::new();
        }
        self.sync_token += 1;
        let mut w = BitWriter::default();
        invest::encode(&mut w, TYPE_SYNC_TOKEN, &Value::Struct(vec![Some(Value::Int(self.sync_token))]));
        vec![(HOST_SYNC_TOKEN, w.finish())]
    }

    /// Host startup request (activity host manager request kind 3), after the kind byte:
    /// a bitstream starting u32, u16 activity index (+0x8000), u16 insertion point (+0x8000).
    pub fn on_startup(&mut self, p: &[u8]) {
        // two length-prefixed blobs: u16 BE length @0 + data @2 (8 bytes: ?, activity index,
        // insertion point, ...), u16 BE length @0x202 + data (~1600 bytes, not yet decoded)
        for at in [0usize, 0x202] {
            if let Some(l) = p.get(at..at + 2).map(|b| u16::from_be_bytes([b[0], b[1]]) as usize) {
                let d = p.get(at + 2..(at + 2 + l).min(p.len())).unwrap_or(&[]);
                info!("activity host: startup blob @{at:#x} ({l} bytes): {}", crate::pb::hex(&d[..d.len().min(64)]));
            }
        }
        if p.len() >= 8 {
            let index = u16::from_be_bytes([p[4], p[5]]) as i32 - 0x8000;
            let insertion = u16::from_be_bytes([p[6], p[7]]) as i32 - 0x8000;
            let name = scenario_for(index).map(|s| s.name).unwrap_or_default();
            info!("activity host: startup for activity index {index} ({name}, hash {:#010x}), insertion point {insertion}",
                  activity_hash(index).unwrap_or(0));
            self.activity = Some((index, insertion));
        }
    }

    /// Handle one client message; returns host messages to send back (type, data).
    pub fn on_client(&mut self, m: &ClientMessage) -> Vec<(u32, Vec<u8>)> {
        match m.ty {
            CLIENT_JOIN_REQUEST => {
                let identity = join_identity(m.data);
                info!("activity host: join request {}", invest::show(&identity));
                self.joined = true;
                let player = match &identity {
                    Value::Struct(f) => f.get(2).cloned().flatten().map(|id| Player {
                        identity: id,
                        properties: f.get(3).cloned().flatten(),
                    }),
                    _ => None,
                };
                vec![
                    (HOST_JOIN_RESULT, join_result(&identity)),
                    (HOST_ENTITY_INDICES, entity_indices()),
                    (HOST_MEMBERSHIP, membership(player.as_slice())),
                    (HOST_INSTANCE, self.instance()),
                ]
                .into_iter()
                .chain(world_globals())
                .chain(claim_abandoned())
                .collect()
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
        let (index, mut insertion) = self.activity.unwrap_or((-1, -1));
        // D1B_INSERTION=<n> (research): answer with this insertion point instead of the
        // requested one (the client asks for -1, "default", which the real host resolves)
        if let Some(n) = std::env::var("D1B_INSERTION").ok().and_then(|v| v.parse().ok()) {
            info!("activity host: insertion point {insertion} -> {n} (D1B_INSERTION)");
            insertion = n;
        }
        match scenario_for(index) {
            Some(sc) => instance(&sc.name, sc.checksum, sc.bubbles, index, insertion),
            None => {
                warn!("activity host: no scenario known for activity index {index}");
                instance("", 0, 0, index, insertion)
            }
        }
    }
}

pub fn entity_indices() -> Vec<u8> {
    // D1B_GRANT_ALL_INDICES (research): grant the host's range too
    let grant_all = std::env::var_os("D1B_GRANT_ALL_INDICES").is_some();
    let words = (0..ENTITY_INDEX_WORDS)
        .map(|i| Some(Value::Int(if CLIENT_INDEX_WORDS.contains(&i) || grant_all { 0xFFFF_FFFF } else { 0 })))
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
