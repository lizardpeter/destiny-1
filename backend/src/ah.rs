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
    /// The activity host instance the message is for.
    pub target: u64,
    pub ty: u32,
    pub data: &'a [u8],
}

/// Parse a client -> host notification payload (after the 14-byte header class 3, whose
/// target id is the first 8 bytes of `payload` here).
pub fn parse_client(payload: &[u8]) -> Option<ClientMessage<'_>> {
    let target = u64::from_be_bytes(payload.get(..8)?.try_into().ok()?);
    let p = payload.get(8..)?;
    if *p.first()? != 1 || p.len() < 13 {
        return None;
    }
    let ty = u32::from_be_bytes(p[1..5].try_into().ok()?);
    let len = u32::from_be_bytes(p[5..9].try_into().ok()?) as usize;
    let data = p.get(13..13 + len)?;
    Some(ClientMessage { target, ty, data })
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
/// @0 u32 change number (see membership_with), @4 u32 (update id; a change resets the
///    client's +0x64B4)
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
fn region_table(regions: &[i64], players: usize, session: Option<&RegionSession>) -> Value {
    use Value::*;
    let tokens: Vec<Option<Value>> = (0..players).map(|_| Some(Int(1))).collect();
    let peers = (1i64 << players) - 1;
    let mut entries: Vec<Option<Value>> = regions
        .iter()
        .map(|&id| {
            // @0x28 {u8, u20, i8[20] transition tokens, session description (0x808043BC: u8
            // count + bytes; the region session's 78-byte data, as the ambassador reports it),
            // i64 public activity host instance}: what citizens join (0x77CD20)
            let (blob, ah) = match session {
                Some(r) => (
                    Struct(vec![
                        Some(Int(r.data.len() as i64)),
                        Some(Array(r.data.iter().map(|&b| Some(Int(b as i64))).collect())),
                    ]),
                    Int(r.host as i64),
                ),
                None => (Struct(vec![Some(Int(0)), Some(Array(vec![]))]), Int(0)),
            };
            Some(Struct(vec![
                Some(Int(id)),
                Some(Int(0)),
                // {u8, i2 ambassador state (1 assigned), i5 ambassador peer slot, bool @0x19
                // "a player reached the matchmaking threshold": the ambassador stops searching
                // for other public sessions and spins up a new one (0x77C3D0, +0x4A9)}. Nobody
                // else is in the region, so there is nothing to find.
                Some(Struct(vec![Some(Int(0)), Some(Int(1)), Some(Int(0)), Some(Bool(true))])),
                Some(Int(peers)),
                Some(Struct(vec![Some(Int(0)), Some(Int(0)), Some(Array(tokens.clone())), Some(blob), Some(ah)])),
            ]))
        })
        .collect();
    while entries.len() < 40 {
        entries.push(Some(Struct(vec![Some(Int(-1))])));
    }
    Struct(vec![Some(Array(entries))])
}

/// A region's public session, as its ambassador reported it.
#[derive(Clone)]
pub struct RegionSession {
    /// 78-byte session data (id, host address, security key)
    pub data: Vec<u8>,
    /// the public activity host instance the ambassador started for it
    pub host: u64,
}

/// The region session description in a client_authoritative_data_update (type 21). The update
/// is delta-encoded against the previous one (0x29D620 -> 0x2C9D20 / 0x2C7FA0, payload type
/// *0x191A300); until that encoding is decoded the description is found by its shape: an
/// 8-bit count 0x4E, then a non-zero 8-byte id and the host's IPv4 address (10.0.2.n).
pub fn find_region_session(data: &[u8]) -> Option<Vec<u8>> {
    // bits past the end read as zero (the encoder drops trailing zero bytes)
    let bit = |i: usize| data.get(i >> 3).map_or(0, |b| (b >> (7 - (i & 7))) & 1);
    let byte_at = |i: usize| (0..8).fold(0u8, |v, k| (v << 1) | bit(i + k));
    let total = data.len() * 8;
    (0..total.saturating_sub(8 + 14 * 8)).find_map(|i| {
        if byte_at(i) != 0x4E {
            return None;
        }
        let d: Vec<u8> = (0..78).map(|k| byte_at(i + 8 + k * 8)).collect();
        (d[..8].iter().any(|&b| b != 0) && d[8] == 10 && d[9] == 0 && d[10] == 2).then_some(d)
    })
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
    membership_with(players, None)
}

pub fn membership_with(players: &[Player], region: Option<&RegionSession>) -> Vec<u8> {
    let slots: Vec<Option<Value>> = players
        .iter()
        .enumerate()
        .map(|(i, p)| {
            // slot state 0x80800C56: {properties, ?, ?, ?} (all optional)
            let state = p.properties.clone().map(|pr| Value::Struct(vec![Some(pr)]));
            // @0x248 (i4, optional) is the slot's boot reason (1 = "debug-command", ...), not an
            // index: a member given 1 there is booted by its own client. Left out.
            let _ = i;
            Some(Value::Struct(vec![Some(p.identity.clone()), state, None]))
        })
        .collect();
    let mask = (1i64 << players.len()) - 1;
    // @0 is the membership's change number: the simulation rebuilds its peer list from the
    // peer mask @0x5028 only when it changes (0xBA3090), so a member added later would never
    // be simulated by the others with a constant one. Every membership sent gets a new number.
    static CHANGE: std::sync::atomic::AtomicI64 = std::sync::atomic::AtomicI64::new(1);
    let change = CHANGE.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let v = Value::Struct(vec![
        Some(Value::Int(change)),
        Some(Value::Int(1)),
        Some(Value::Array(slots)),
        Some(region_table(&[0], players.len(), region)),
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
    /// checksum of a private instance; a public one is checked against `checksum_public`
    /// (the client indexes the tag's checksums by its activity client kind: 0x299B00)
    pub checksum: u32,
    pub checksum_public: u32,
    pub bubbles: u32,
}

#[derive(serde::Deserialize)]
struct ActivityRow {
    index: i32,
    hash: String,
    name: Option<String>,
    checksum: Option<String>,
    checksum_public: Option<String>,
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
    Some(Scenario {
        name: r.name.clone()?,
        checksum: hex_u32(r.checksum.as_deref()?)?,
        checksum_public: hex_u32(r.checksum_public.as_deref()?)?,
        bubbles: r.bubbles?,
    })
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

/// Client -> host: client_authoritative_data_update (delta-encoded client data).
pub const CLIENT_AUTHORITATIVE_DATA_UPDATE: u32 = 21;
/// Client -> host: request_peer_reservation (payload 0x80800BB9).
pub const CLIENT_REQUEST_PEER_RESERVATION: u32 = 12;
const TYPE_PEER_RESERVATION: &str = "0x80800bb9";

/// A citizen joining a public instance names the private instance it comes from (properties
/// @0x18) but carries no fireteam id (identity member 5, properties @0xA0: 0). The fireteam id
/// is what the world controller groups players by (0x75F210, "fireteam_from_player"), and the
/// simulation only creates a remote player once it has one (0xBA6830): the public host gives
/// the player the fireteam id it has in its private instance.
fn inherit_fireteam(all: &std::collections::HashMap<u64, Instance>, p: &mut Player) {
    let int_at = |v: &Option<Value>, i: usize| match v {
        Some(Value::Struct(f)) => match f.get(i) {
            Some(Some(Value::Int(n))) => Some(*n),
            _ => None,
        },
        _ => None,
    };
    let props = p.properties.clone();
    if int_at(&props, 5) != Some(0) {
        return;
    }
    let Some(parent) = int_at(&props, 3).filter(|&n| n != 0) else { return };
    let machine = machine_of(&p.identity);
    let Some(fireteam) = all.get(&(parent as u64)).and_then(|i| {
        i.members
            .iter()
            .find(|(_, q, _)| machine_of(&q.identity) == machine)
            .and_then(|(_, q, _)| int_at(&q.properties, 5).or_else(|| int_at(&Some(q.identity.clone()), 4)))
    }) else {
        return;
    };
    if fireteam == 0 {
        return;
    }
    info!("activity host: player from instance {parent:#x} keeps fireteam {fireteam:#x}");
    if let Some(Value::Struct(f)) = p.properties.as_mut() {
        f[5] = Some(Value::Int(fireteam));
    }
    if let Value::Struct(f) = &mut p.identity {
        if f.len() > 4 {
            f[4] = Some(Value::Int(fireteam));
        }
    }
}

/// The machine id (first member) of an identity block 0x80800C2D.
fn machine_of(identity: &Value) -> Option<Value> {
    match identity {
        Value::Struct(f) => f.first().cloned().flatten(),
        _ => None,
    }
}

/// Instance kinds (host startup blob byte 4; the client's activity client kind + 1).
pub const INSTANCE_PRIVATE: u8 = 1;
pub const INSTANCE_PUBLIC: u8 = 2;

/// Host messages pushed to a connection from elsewhere (another member joining, ...).
pub type Push = tokio::sync::mpsc::UnboundedSender<(u32, Vec<u8>)>;

/// An activity host instance: created by a host startup (the session host's activity
/// client), joined by every member's activity client (one BAP connection each).
struct Instance {
    activity: (i32, i32),
    /// instance kind from the host startup (INSTANCE_PRIVATE / INSTANCE_PUBLIC)
    kind: u8,
    /// (connection id, player, push channel), in slot order; a reserved slot (requested by
    /// the session host for a fireteam member that has not joined yet) has connection 0 and
    /// no channel
    members: Vec<(u64, Player, Option<Push>)>,
    /// the public region's session, once its ambassador reported it
    region: Option<RegionSession>,
}

impl Instance {
    fn membership(&self) -> Vec<u8> {
        let players: Vec<Player> = self.members.iter().map(|(_, p, _)| p.clone()).collect();
        membership_with(&players, self.region.as_ref())
    }
    /// Send the current membership to every member except `skip`.
    fn push_membership(&self, skip: u64) -> Vec<u8> {
        let m = self.membership();
        for (c, _, push) in &self.members {
            if *c != skip {
                if let Some(push) = push {
                    let _ = push.send((HOST_MEMBERSHIP, m.clone()));
                }
            }
        }
        m
    }
}

fn instances() -> &'static std::sync::Mutex<std::collections::HashMap<u64, Instance>> {
    static I: std::sync::OnceLock<std::sync::Mutex<std::collections::HashMap<u64, Instance>>> = std::sync::OnceLock::new();
    I.get_or_init(Default::default)
}

static NEXT_CONNECTION: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(1);

/// Per-connection activity host state.
pub struct Host {
    logged: std::collections::HashSet<u32>,
    /// From the host startup request (or the instance this connection joined): activity index
    /// and insertion point.
    activity: Option<(i32, i32)>,
    /// instance kind (startup blob byte 4): 1 private, 2 public
    kind: u8,
    joined: bool,
    sync_token: i64,
    /// Instance this connection talks to, and its own id and push channel.
    instance: u64,
    connection: u64,
    push: Option<Push>,
}

impl Default for Host {
    fn default() -> Self {
        Host {
            logged: Default::default(),
            activity: None,
            kind: INSTANCE_PRIVATE,
            joined: false,
            sync_token: 0,
            instance: 0,
            connection: NEXT_CONNECTION.fetch_add(1, std::sync::atomic::Ordering::Relaxed),
            push: None,
        }
    }
}

impl Drop for Host {
    fn drop(&mut self) {
        // leave the instance; the others get the membership without this player
        let mut all = instances().lock().unwrap();
        if let Some(inst) = all.get_mut(&self.instance) {
            let before = inst.members.len();
            inst.members.retain(|(c, _, _)| *c != self.connection);
            if inst.members.len() != before {
                info!("activity host: instance {:#x}: a player left ({} remain)", self.instance, inst.members.len());
                let m = inst.membership();
                for (_, _, push) in &inst.members {
                    if let Some(push) = push {
                        let _ = push.send((HOST_MEMBERSHIP, m.clone()));
                    }
                }
            }
        }
    }
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
    /// a bitstream starting u16, u16 activity index (+0x8000), u16 insertion point (+0x8000),
    /// u8 instance kind (1 private, 2 public).
    pub fn on_startup(&mut self, p: &[u8]) {
        // two length-prefixed blobs: u16 BE length @0 + data @2 (8 bytes: ?, activity index,
        // insertion point, ...), u16 BE length @0x202 + data (~1600 bytes, not yet decoded)
        for at in [0usize, 0x202] {
            if let Some(l) = p.get(at..at + 2).map(|b| u16::from_be_bytes([b[0], b[1]]) as usize) {
                let d = p.get(at + 2..(at + 2 + l).min(p.len())).unwrap_or(&[]);
                info!("activity host: startup blob @{at:#x} ({l} bytes): {}", crate::pb::hex(&d[..d.len().min(64)]));
            }
        }
        if p.len() >= 9 {
            let index = u16::from_be_bytes([p[4], p[5]]) as i32 - 0x8000;
            let insertion = u16::from_be_bytes([p[6], p[7]]) as i32 - 0x8000;
            let name = scenario_for(index).map(|s| s.name).unwrap_or_default();
            info!("activity host: startup for activity index {index} ({name}, hash {:#010x}), insertion point {insertion}",
                  activity_hash(index).unwrap_or(0));
            self.activity = Some((index, insertion));
            self.kind = p[8];
            info!("activity host: instance kind {}", self.kind);
        }
    }

    /// The host startup was answered with instance id `id`: create the instance.
    pub fn register(&mut self, id: u64) {
        self.instance = id;
        if let Some(a) = self.activity {
            instances().lock().unwrap().insert(id, Instance { activity: a, kind: self.kind, members: Vec::new(), region: None });
        }
    }

    /// A message for instance `target` arrived on this connection (a member's activity client
    /// connects and joins without a startup of its own).
    pub fn bind(&mut self, target: u64, push: &Push) {
        if self.push.is_none() {
            self.push = Some(push.clone());
        }
        if self.instance == 0 || self.activity.is_none() {
            if let Some(inst) = instances().lock().unwrap().get(&target) {
                self.instance = target;
                self.activity = Some(inst.activity);
                self.kind = inst.kind;
                info!("activity host: connection joins instance {target:#x} (activity {:?})", inst.activity);
            }
        }
    }

    /// The instance this connection talks to (0 before a startup or a bound message).
    pub fn instance_id(&self) -> u64 {
        self.instance
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
                // add the player to the instance; everyone already there gets the new membership
                let players: Vec<Player> = {
                    let mut all = instances().lock().unwrap();
                    match (all.contains_key(&self.instance), player.clone(), self.push.clone()) {
                        (true, Some(mut p), Some(push)) => {
                            inherit_fireteam(&all, &mut p);
                            let inst = all.get_mut(&self.instance).expect("checked above");
                            inst.members.retain(|(c, _, _)| *c != self.connection);
                            // a slot reserved for this machine is taken over in place
                            let machine = machine_of(&p.identity);
                            match inst.members.iter_mut().find(|(c, q, _)| *c == 0 && machine_of(&q.identity) == machine) {
                                Some(slot) => *slot = (self.connection, p, Some(push)),
                                None => inst.members.push((self.connection, p, Some(push))),
                            }
                            let players: Vec<Player> = inst.members.iter().map(|(_, p, _)| p.clone()).collect();
                            let m = inst.membership();
                            for (c, _, push) in &inst.members {
                                if *c != self.connection {
                                    if let Some(push) = push {
                                        let _ = push.send((HOST_MEMBERSHIP, m.clone()));
                                    }
                                }
                            }
                            info!("activity host: instance {:#x} now has {} players", self.instance, players.len());
                            let activity = inst.activity;
                            let me = self.instance;
                            let this_machine = machine.clone();
                            // a player joining a second instance of the same activity: that is the
                            // public host of the region the first instance's region entry names
                            let private = all
                                .iter()
                                // same activity index (the public client asks with insertion point -1)
                                .filter(|(id, i)| **id < me && i.activity.0 == activity.0)
                                .filter(|(_, i)| i.members.iter().any(|(_, p, _)| machine_of(&p.identity) == this_machine))
                                .map(|(id, _)| *id)
                                .max();
                            if let Some(pid) = private {
                                if let Some(pi) = all.get_mut(&pid) {
                                    let r = pi.region.get_or_insert(RegionSession { data: Vec::new(), host: 0 });
                                    if r.host != me {
                                        r.host = me;
                                        info!("activity host: instance {pid:#x}: region public host {me:#x}");
                                        pi.push_membership(0);
                                    }
                                }
                            }
                            players
                        }
                        _ => player.into_iter().collect(),
                    }
                };
                vec![
                    (HOST_JOIN_RESULT, join_result(&identity)),
                    (HOST_ENTITY_INDICES, entity_indices()),
                    (HOST_MEMBERSHIP, {
                        let all = instances().lock().unwrap();
                        membership_with(&players, all.get(&self.instance).and_then(|i| i.region.as_ref()))
                    }),
                    (HOST_INSTANCE, self.instance()),
                ]
                .into_iter()
                .chain(world_globals())
                .chain(claim_abandoned())
                .collect()
            }
            CLIENT_AUTHORITATIVE_DATA_UPDATE => {
                let Some(data) = find_region_session(m.data) else {
                    return Vec::new();
                };
                let mut all = instances().lock().unwrap();
                // the public host is linked when the ambassador joins it (see join)
                let host = all.get(&self.instance).and_then(|i| i.region.as_ref()).map_or(0, |r| r.host);
                if let Some(inst) = all.get_mut(&self.instance) {
                    let changed = inst.region.as_ref().map_or(true, |r| r.data != data || r.host != host);
                    if changed {
                        info!("activity host: instance {:#x}: region session {} on public host {host:#x}",
                              self.instance, crate::pb::hex(&data[..8]));
                        inst.region = Some(RegionSession { data, host });
                        return vec![(HOST_MEMBERSHIP, inst.push_membership(self.connection))];
                    }
                }
                Vec::new()
            }
            CLIENT_REQUEST_PEER_RESERVATION => {
                // {u32 request, {count, up to 20 {.., identity 0x80800C2D}}} (0x80800BB9): the
                // session host reserves slots for its fireteam members before they join; the
                // membership then lists them, which is what lets their activity clients start
                // ("waiting for session host to include us in the registered peer mask").
                let v = invest::decode(&mut BitReader::new(m.data), TYPE_PEER_RESERVATION);
                let ids: Vec<Value> = match &v {
                    Value::Struct(f) => match f.get(1).cloned().flatten() {
                        Some(Value::Struct(g)) => match g.get(1).cloned().flatten() {
                            Some(Value::Array(a)) => a
                                .into_iter()
                                .flatten()
                                // each element is (or wraps) the identity block
                                .filter_map(|e| match e {
                                    Value::Struct(x) if x.len() == 1 => x[0].clone(),
                                    v @ Value::Struct(_) => Some(v),
                                    _ => None,
                                })
                                .collect(),
                            _ => vec![],
                        },
                        _ => vec![],
                    },
                    _ => vec![],
                };
                info!("activity host: instance {:#x}: peer reservation for {} players: {}", self.instance, ids.len(),
                      invest::show(&v));
                let mut all = instances().lock().unwrap();
                if let Some(inst) = all.get_mut(&self.instance) {
                    for id in ids {
                        let machine = machine_of(&id);
                        if !inst.members.iter().any(|(_, q, _)| machine_of(&q.identity) == machine) {
                            inst.members.push((0, Player { identity: id, properties: None }, None));
                        }
                    }
                    let mm = inst.membership();
                    for (c, _, push) in &inst.members {
                        if *c != self.connection {
                            if let Some(push) = push {
                                let _ = push.send((HOST_MEMBERSHIP, mm.clone()));
                            }
                        }
                    }
                    return vec![(HOST_MEMBERSHIP, mm)];
                }
                Vec::new()
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
            Some(sc) => {
                let checksum = if self.kind == INSTANCE_PUBLIC { sc.checksum_public } else { sc.checksum };
                instance(&sc.name, checksum, sc.bubbles, index, insertion)
            }
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

    #[test]
    fn region_session_in_authoritative_update() {
        // captured client_authoritative_data_update (type 21) after the ambassador created
        // its region session 883CD132:F8AC8803 at 10.0.2.15:3074
        let p = crate::pb::unhex("a802000000010000000128049d1079a265f15910061400041e041801fe01fe000001fe01fe00001400041e041805a23f89fd8e0400000000005881226e3b7eac11bd58eccabcc14e24000000000000000000000000000000");
        let d = find_region_session(&p).expect("session description");
        assert_eq!(d.len(), 78);
        assert_eq!(&d[..8], &[0x88, 0x3c, 0xd1, 0x32, 0xf8, 0xac, 0x88, 0x03]);
        assert_eq!(&d[8..14], &[10, 0, 2, 15, 0x02, 0x0c]);
    }
}
