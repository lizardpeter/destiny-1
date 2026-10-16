//! Investment ("world server") messages carried in BAP client_to_world_server_request (10) /
//! response (11).
//!
//! Payload (writer 0x261E90, reader 0x262260): an MSB-first bitstream
//! ```text
//! u16  server message id (0x01F7 ...)
//! ...  request or response struct, serialized from the engine's type descriptors
//! 1    has_extra; if set: u16 length + bytes
//! ```
//! The message table (id -> request/response type) lives in the investment globals content;
//! `data/investment_schema.json` is a dump of it and of every type it reaches (taken from the
//! running client, see findings/LOG.md). Type descriptors (reader 0x101EB30, per-kind
//! handlers at 0x19131B0): a struct is a list of members; a member with `pres` is preceded
//! by a presence bit; kind 1 nests another type. A type with `array` is a fixed array of
//! its single member (`off` = stride); a kind-1 member with `count_at` holds a variable
//! count read from the int at that offset of the enclosing struct. Numbers are written as
//! `value + bias` in `bits` bits (kinds 3/7 int8, 4/8 int16, 5/9 int32, 6/10 int64), kind 2
//! is one bit, kind 11 a raw 32-bit float.

use serde::Deserialize;
use std::{collections::HashMap, sync::OnceLock};

#[derive(Deserialize)]
pub struct Schema {
    pub families: Vec<FamilySlot>,
    pub messages: HashMap<String, MessageDef>,
    pub types: HashMap<String, TypeDef>,
}

#[derive(Deserialize)]
pub struct MessageDef {
    pub req: String,
    pub res: String,
}

/// Object types each server-object family holds (object manager +0x4FD90: 6 slots per family).
#[derive(Deserialize)]
pub struct FamilySlot {
    pub family: u32,
    pub slot: u32,
    pub max: u32,
    #[serde(rename = "type")]
    pub ty: String,
}

#[derive(Deserialize, Default)]
pub struct TypeDef {
    #[serde(default)]
    pub hash: String,
    #[serde(default)]
    pub size: u32,
    #[serde(default)]
    pub array: u32,
    #[serde(default)]
    pub members: Vec<Member>,
}

#[derive(Deserialize, Clone)]
pub struct Member {
    pub kind: u8,
    pub off: i32,
    #[serde(default)]
    pub pres: u8,
    #[serde(rename = "type")]
    pub ty: Option<String>,
    pub count_at: Option<i32>,
    #[serde(default)]
    pub bias: i32,
    #[serde(default)]
    pub bits: u32,
    /// Third parameter word: for floats (kind 11) the quantized bit count (0 or 32 = raw).
    #[serde(default)]
    pub p2: i32,
}

pub fn schema() -> &'static Schema {
    static S: OnceLock<Schema> = OnceLock::new();
    S.get_or_init(|| serde_json::from_str(include_str!("../data/investment_schema.json")).expect("investment schema"))
}

fn ty(id: &str) -> &'static TypeDef {
    schema().types.get(id).unwrap_or_else(|| panic!("investment type {id} missing from schema"))
}

/// A decoded/encodable value. Structs are positional (one entry per member, `None` = absent
/// optional member); arrays hold their elements.
#[derive(Clone, Debug, PartialEq)]
pub enum Value {
    Int(i64),
    Bool(bool),
    Float(f32),
    Struct(Vec<Option<Value>>),
    Array(Vec<Option<Value>>),
}

impl Value {
    pub fn int(&self) -> i64 {
        match self {
            Value::Int(v) => *v,
            Value::Bool(b) => *b as i64,
            _ => 0,
        }
    }
}

#[derive(Default)]
pub struct BitWriter {
    out: Vec<u8>,
    acc: u64,
    n: u32,
}

impl BitWriter {
    pub fn bits(&mut self, v: u64, bits: u32) {
        for i in (0..bits).rev() {
            self.acc = (self.acc << 1) | ((v >> i) & 1);
            self.n += 1;
            if self.n == 8 {
                self.out.push(self.acc as u8);
                self.acc = 0;
                self.n = 0;
            }
        }
    }
    pub fn bit(&mut self, b: bool) {
        self.bits(b as u64, 1);
    }
    pub fn finish(mut self) -> Vec<u8> {
        if self.n > 0 {
            self.out.push((self.acc << (8 - self.n)) as u8);
        }
        self.out
    }
}

pub struct BitReader<'a> {
    data: &'a [u8],
    pos: usize,
    pub overrun: bool,
}

impl<'a> BitReader<'a> {
    pub fn new(data: &'a [u8]) -> Self {
        BitReader { data, pos: 0, overrun: false }
    }
    pub fn bits(&mut self, bits: u32) -> u64 {
        let mut v = 0u64;
        for _ in 0..bits {
            let b = match self.data.get(self.pos / 8) {
                Some(byte) => (byte >> (7 - self.pos % 8)) & 1,
                None => {
                    self.overrun = true;
                    0
                }
            };
            v = (v << 1) | b as u64;
            self.pos += 1;
        }
        v
    }
    pub fn bit(&mut self) -> bool {
        self.bits(1) == 1
    }
    pub fn remaining_bits(&self) -> usize {
        (self.data.len() * 8).saturating_sub(self.pos)
    }
}

fn mask(bits: u32) -> u64 {
    if bits >= 64 { u64::MAX } else { (1u64 << bits) - 1 }
}

fn encode_scalar(w: &mut BitWriter, m: &Member, v: Option<&Value>) {
    let v = v.cloned().unwrap_or(Value::Int(0));
    match m.kind {
        2 => w.bit(v.int() != 0),
        11 => w.bits(match v { Value::Float(f) => f.to_bits() as u64, other => (other.int() as f32).to_bits() as u64 }, 32),
        3..=10 => w.bits((v.int().wrapping_add(m.bias as i64)) as u64 & mask(m.bits), m.bits),
        // type handle (0x102C1D0): presence bit, then u32; -1 = absent
        23 => {
            let t = v.int() as u32;
            w.bit(t != u32::MAX);
            if t != u32::MAX {
                w.bits(t as u64, 32);
            }
        }
        // 8-byte identifier (0x102D280 -> 0x808004AC: u8[8] in memory order)
        35 => {
            for b in (v.int() as u64).to_le_bytes() {
                w.bits(b as u64, 8);
            }
        }
        k => panic!("investment kind {k} not supported for encoding"),
    }
}

fn decode_scalar(r: &mut BitReader, m: &Member) -> Value {
    match m.kind {
        2 => Value::Bool(r.bit()),
        11 if m.p2 > 0 && m.p2 < 32 => Value::Int(r.bits(m.p2 as u32) as i64), // quantized (0x72C20)
        11 => Value::Float(f32::from_bits(r.bits(32) as u32)),
        3..=10 => {
            let raw = r.bits(m.bits) as i64;
            let v = raw.wrapping_sub(m.bias as i64);
            // sign-extend to the field width (8/16/32/64 by kind)
            let w = match m.kind { 3 | 7 => 8, 4 | 8 => 16, 5 | 9 => 32, _ => 64 };
            Value::Int(if w == 64 { v } else { ((v << (64 - w)) >> (64 - w)) as i64 })
        }
        23 => Value::Int(if r.bit() { r.bits(32) as u32 as i64 } else { -1 }),
        35 => {
            let mut b = [0u8; 8];
            for x in &mut b {
                *x = r.bits(8) as u8;
            }
            Value::Int(u64::from_le_bytes(b) as i64)
        }
        // Kinds below: per-kind decoders in the client's table at 0x1913060 (decoded 2026-10-15).
        0 | 17 => Value::Int(0), // nothing on the wire
        12 => Value::Int(r.bits(64) as i64),
        // point3d (0x2CA900): 3 x 32 bits unless world-position quantization is on
        // (0x267FB28, off in practice)
        13 => Value::Struct((0..3).map(|_| Some(Value::Float(f32::from_bits(r.bits(32) as u32)))).collect()),
        // vector3d (0x72D90): bit "zero"; else 19-bit direction + 16-bit length
        14 => {
            if r.bit() {
                Value::Int(0)
            } else {
                let dir = r.bits(19);
                let len = r.bits(16);
                Value::Struct(vec![Some(Value::Int(dir as i64)), Some(Value::Int(len as i64))])
            }
        }
        18 | 20 | 21 | 22 => Value::Int(if r.bit() { r.bits(32) as u32 as i64 } else { -1 }),
        19 => {
            if r.bit() {
                let h = r.bits(32);
                let k = r.bits(6);
                Value::Struct(vec![Some(Value::Int(h as i64)), Some(Value::Int(k as i64))])
            } else {
                Value::Int(-1)
            }
        }
        // variant: 6-bit kind, then a value of that kind
        24 | 25 => {
            let k = r.bits(6) as u8;
            let mut inner = m.clone();
            inner.kind = k;
            decode_scalar(r, &inner)
        }
        26 => Value::Struct(vec![Some(Value::Int(r.bits(64) as i64)), Some(Value::Int(r.bits(64) as i64))]),
        27 | 28 => {
            if !r.bit() {
                Value::Int(-1)
            } else if !r.bit() {
                Value::Struct((0..3).map(|_| Some(Value::Int(r.bits(64) as i64))).collect())
            } else {
                Value::Struct(vec![Some(Value::Int(r.bits(32) as i64)), Some(Value::Int(r.bits(32) as i64)), Some(Value::Int(r.bits(12) as i64))])
            }
        }
        29 => {
            let h = if r.bit() { Some(Value::Int(((r.bits(32) << 6) | r.bits(6)) as i64)) } else { None };
            Value::Struct(vec![h, Some(Value::Int(r.bits(64) as i64)), Some(Value::Int(r.bits(64) as i64))])
        }
        // typed value: type handle (0x80800046), then that type
        34 | 41 => {
            let t = if r.bit() { r.bits(32) as u32 } else { u32::MAX };
            if t == u32::MAX {
                Value::Int(-1)
            } else {
                let id = format!("{t:#010x}");
                if schema().types.contains_key(&id) { decode(r, &id) } else { Value::Int(t as i64) }
            }
        }
        k => panic!("investment kind {k} not supported for decoding"),
    }
}

/// Number of elements of a nested array member, given the already-encoded sibling values.
fn element_count(t: &TypeDef, m: &Member, parent: &TypeDef, siblings: &[Option<Value>]) -> usize {
    match m.count_at {
        Some(off) => parent
            .members
            .iter()
            .position(|s| s.off == off)
            .and_then(|i| siblings.get(i).cloned().flatten())
            .map(|v| v.int().max(0) as usize)
            .unwrap_or(0)
            .min(t.array as usize),
        None => t.array as usize,
    }
}

pub fn encode(w: &mut BitWriter, type_id: &str, v: &Value) {
    let t = ty(type_id);
    let fields: &[Option<Value>] = match v {
        Value::Struct(f) | Value::Array(f) => f,
        _ => &[],
    };
    encode_members(w, t, fields);
}

fn encode_members(w: &mut BitWriter, t: &TypeDef, fields: &[Option<Value>]) {
    if t.array > 0 {
        // Fixed array; the caller chose how many elements to write.
        let m = &t.members[0];
        for e in fields {
            encode_member(w, m, e.as_ref(), t, &[]);
        }
        return;
    }
    for (i, m) in t.members.iter().enumerate() {
        encode_member(w, m, fields.get(i).and_then(|f| f.as_ref()), t, &fields[..i.min(fields.len())]);
    }
}

fn encode_member(w: &mut BitWriter, m: &Member, v: Option<&Value>, parent: &TypeDef, siblings: &[Option<Value>]) {
    if m.pres != 0 {
        w.bit(v.is_some());
        if v.is_none() {
            return;
        }
    }
    if m.kind == 1 {
        let sub = ty(m.ty.as_deref().unwrap());
        let fields: Vec<Option<Value>> = match v {
            Some(Value::Struct(f)) | Some(Value::Array(f)) => f.clone(),
            _ => Vec::new(),
        };
        if sub.array > 0 {
            let n = element_count(sub, m, parent, siblings);
            let mut elems = fields;
            elems.resize(n, None);
            // an absent element of a non-optional array is written as zero
            let em = &sub.members[0];
            let zero = Value::Int(0);
            for e in &elems {
                let e = e.as_ref().or(if em.pres != 0 { None } else { Some(&zero) });
                encode_member(w, em, e, sub, &[]);
            }
        } else {
            encode_members(w, sub, &fields);
        }
    } else {
        encode_scalar(w, m, v);
    }
}

pub fn decode(r: &mut BitReader, type_id: &str) -> Value {
    let t = ty(type_id);
    Value::Struct(decode_members(r, t))
}

fn decode_members(r: &mut BitReader, t: &TypeDef) -> Vec<Option<Value>> {
    let mut out: Vec<Option<Value>> = Vec::with_capacity(t.members.len());
    for m in &t.members {
        let v = decode_member(r, m, t, &out);
        out.push(v);
    }
    out
}

fn decode_member(r: &mut BitReader, m: &Member, parent: &TypeDef, siblings: &[Option<Value>]) -> Option<Value> {
    if m.pres != 0 && !r.bit() {
        return None;
    }
    if r.overrun {
        return None;
    }
    if m.kind == 1 {
        let sub = ty(m.ty.as_deref().unwrap());
        if sub.array > 0 {
            let n = element_count(sub, m, parent, siblings);
            let em = &sub.members[0];
            let elems = (0..n).map(|_| decode_member(r, em, sub, &[])).collect();
            Some(Value::Array(elems))
        } else {
            Some(Value::Struct(decode_members(r, sub)))
        }
    } else {
        Some(decode_scalar(r, m))
    }
}

/// Short text form of a value; int8 arrays print as strings.
pub fn show(v: &Value) -> String {
    match v {
        Value::Int(i) => i.to_string(),
        Value::Bool(b) => b.to_string(),
        Value::Float(f) => format!("{f}"),
        Value::Struct(f) => format!("{{{}}}", f.iter().map(|x| x.as_ref().map(show).unwrap_or("-".into())).collect::<Vec<_>>().join(", ")),
        Value::Array(e) => {
            let bytes: Option<Vec<u8>> = e.iter().map(|x| match x { Some(Value::Int(i)) if (0..256).contains(i) => Some(*i as u8), _ => None }).collect();
            match bytes {
                Some(b) if !b.is_empty() && b[0].is_ascii_graphic() => {
                    let end = b.iter().position(|&c| c == 0).unwrap_or(b.len());
                    format!("{:?}", String::from_utf8_lossy(&b[..end]))
                }
                _ => format!("[{}]", e.iter().map(|x| x.as_ref().map(show).unwrap_or("-".into())).collect::<Vec<_>>().join(", ")),
            }
        }
    }
}

/// Parsed world server request: message id, its decoded request struct, extra bytes.
pub struct Request {
    pub id: u16,
    pub body: Option<Value>,
    pub extra: Option<Vec<u8>>,
}

pub fn parse_request(payload: &[u8]) -> Request {
    let mut r = BitReader::new(payload);
    let id = r.bits(16) as u16;
    let body = schema().messages.get(&format!("{id:#x}")).map(|d| decode(&mut r, &d.req));
    let extra = if r.bit() {
        let n = r.bits(16) as usize;
        Some((0..n).map(|_| r.bits(8) as u8).collect())
    } else {
        None
    };
    Request { id, body, extra }
}

/// World server response payload for message `id` carrying `body` (response type).
pub fn response(id: u16, body: &Value) -> Vec<u8> {
    response_with_extra(id, body, None)
}

/// Response with the optional extra blob (u16 length + bytes). Family subscriptions (0xCE)
/// carry the family's queuez update there: the client decodes it with the message-123 class
/// and applies it (0x571150 -> 0x571BE0 -> 0x566050).
pub fn response_with_extra(id: u16, body: &Value, extra: Option<&[u8]>) -> Vec<u8> {
    let def = &schema().messages[&format!("{id:#x}")];
    let mut w = BitWriter::default();
    w.bits(id as u64, 16);
    encode(&mut w, &def.res, body);
    w.bit(extra.is_some());
    if let Some(e) = extra {
        w.bits(e.len() as u64, 16);
        for &b in e {
            w.bits(b as u64, 8);
        }
    }
    w.finish()
}

/// A response with every optional member absent and every number zero.
pub fn empty_response(id: u16) -> Vec<u8> {
    response(id, &Value::Struct(Vec::new()))
}

/// One object of a queuez family update: its type, id and value.
pub struct Object {
    pub ty: &'static str,
    pub soid: i64,
    pub value: Value,
}

/// A family update ("transaction") of a queuez update notification (BAP message 123).
pub struct FamilyUpdate {
    pub family: u32,
    pub root: i64,
    pub version: i32,
    /// bit 0: baseline (full state) rather than a delta
    pub flags: u8,
    pub objects: Vec<Object>,
}

/// queuez_to_client_update_notification payload (decoder 0x56A0C0, reader 0x566050/0x5662D0):
/// ```text
/// u32 BE transaction count (non-zero)
/// per transaction: u32 BE family type, u64 BE family root soid, i32 BE version
///                  (-1 = none), u8 flags, u32 BE object count
///   per object:    u32 BE type hash, u64 BE soid, u32 BE payload length, payload
/// ```
/// An object payload is the bitstream of its type; its first member must be its soid
/// (0x56C780). Objects of length 0 are removals (0x56CDA0).
pub fn queuez_update(updates: &[FamilyUpdate]) -> Vec<u8> {
    let mut out = Vec::new();
    out.extend_from_slice(&(updates.len() as u32).to_be_bytes());
    for u in updates {
        out.extend_from_slice(&u.family.to_be_bytes());
        out.extend_from_slice(&u.root.to_be_bytes());
        out.extend_from_slice(&u.version.to_be_bytes());
        out.push(u.flags);
        out.extend_from_slice(&(u.objects.len() as u32).to_be_bytes());
        for o in &u.objects {
            let hash = u32::from_str_radix(ty(o.ty).hash.trim_start_matches("0x"), 16).unwrap_or(0);
            let mut w = BitWriter::default();
            encode(&mut w, o.ty, &o.value);
            let payload = w.finish();
            out.extend_from_slice(&hash.to_be_bytes());
            out.extend_from_slice(&o.soid.to_be_bytes());
            out.extend_from_slice(&(payload.len() as u32).to_be_bytes());
            out.extend_from_slice(&payload);
        }
    }
    out
}

/// Family 3 (account): root object 0x80801951 {soid, {character count, character ids},
/// ...} and up to 10 character summaries 0x80801954.
pub const FAMILY_ACCOUNT: u32 = 3;
pub const TYPE_ACCOUNT: &str = "0x80801951";

pub const TYPE_CHARACTER_SUMMARY: &str = "0x80801954";

pub const TYPE_CREATE_REQUEST: &str = "0x80801860";

/// Characters on the account. D1B_TEST_CHARACTER=1 adds a default one when there is none
/// (headless tests, which cannot drive the creation screens).
pub fn characters() -> Vec<crate::account::Character> {
    let mut list = crate::account::characters();
    if list.is_empty() && std::env::var("D1B_TEST_CHARACTER").map(|v| v != "0").unwrap_or(false) {
        // stored like a created one, so its client state persists
        let ch = crate::account::Character { id: first_character_id(), creation: TEST_CHARACTER_CREATION.into(), client_state: None };
        crate::account::with(|a| a.characters.push(ch.clone()));
        list.push(ch);
    }
    list
}
/// The test character's creation request: one made on the creation screens (race, gender,
/// class and appearance). An empty request leaves the player's configuration unset (player
/// +0x850 race/gender/class 0xFF, +0x1660 -1), and such a player never gets a unit: the
/// world loads but stays black.
const TEST_CHARACTER_CREATION: &str =
    "c0e0303045b0301030e250e490ce10ea70ea90eaafffeffff0e6d0def02393b8ae3faf0f97274f0f74040404040404040400";
/// Set when a client state report changed the profile; the connection then pushes it.
static PROFILE_DIRTY: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
pub fn take_profile_dirty() -> bool {
    PROFILE_DIRTY.swap(false, std::sync::atomic::Ordering::Relaxed)
}

const TYPE_ACCOUNT_CLIENT_STATE: &str = "0x80801716";
const TYPE_CHARACTER_CLIENT_STATE: &str = "0x8080193c";

fn stored_state(hex_state: Option<String>, ty: &str) -> Option<Value> {
    let bytes = unhex(&hex_state?);
    Some(decode(&mut BitReader::new(&bytes), ty))
}

/// D1B_TEST_CHARACTER accounts start with every "seen" bit of the account client state set
/// (0x8080172C: 128 x u64 and 4 x u32; dismissing the Destiny 2 offer sets bits 11/15/16 of
/// u32 [0], "Armsday" lives in the u32s too), so the one-time screens (the Destiny 2 pre-order offer, Armsday,
/// ...) do not queue up in front of a test. The client's own reports replace it.
fn test_account_state() -> Option<Value> {
    use Value::*;
    if !std::env::var("D1B_TEST_CHARACTER").map(|v| v != "0").unwrap_or(false) {
        return None;
    }
    let words = Array((0..128).map(|_| Some(Int(-1))).collect());
    Some(Struct(vec![Some(Struct(vec![Some(words), Some(Array((0..4).map(|_| Some(Int(0xFFFF_FFFF))).collect()))])), None]))
}

/// Store a reported client state (0x2BD account, 0x2BE active character); true if changed.
fn store_client_state(id: u16, v: &Value) -> bool {
    let ty = if id == 0x2bd { TYPE_ACCOUNT_CLIENT_STATE } else { TYPE_CHARACTER_CLIENT_STATE };
    let mut w = BitWriter::default();
    encode(&mut w, ty, v);
    let h = hex(&w.finish());
    crate::account::with(|a| {
        let slot = if id == 0x2bd { Some(&mut a.client_state) } else { a.characters.last_mut().map(|c| &mut c.client_state) };
        match slot {
            Some(cur) if cur.as_deref() != Some(h.as_str()) => {
                *cur = Some(h);
                true
            }
            _ => false,
        }
    })
}

pub const FIRST_CHARACTER_ID_BASE: i64 = 0x4D31_0000_0000_0100;
/// The current player's first character id (slot n: base + n << 32).
pub fn first_character_id() -> i64 {
    FIRST_CHARACTER_ID_BASE + crate::account::id_offset()
}

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect()
}
fn unhex(s: &str) -> Vec<u8> {
    (0..s.len() / 2).filter_map(|i| u8::from_str_radix(&s[2 * i..2 * i + 2], 16).ok()).collect()
}

/// The creation request's {race/gender/class} and appearance, as stored for a character.
fn creation(ch: &crate::account::Character) -> (Option<Value>, Option<Value>) {
    let bytes = unhex(&ch.creation);
    let mut r = BitReader::new(&bytes);
    match decode(&mut r, TYPE_CREATE_REQUEST) {
        Value::Struct(f) => (f.first().cloned().flatten(), f.get(1).cloned().flatten()),
        _ => (None, None),
    }
}

/// {count, ids[10]} as used by the account summary and the profile.
fn character_list() -> Value {
    use Value::*;
    let ids: Vec<i64> = characters().iter().map(|c| c.id).collect();
    Struct(vec![Some(Int(ids.len() as i64)), Some(Array(ids.iter().map(|&i| Some(Int(i))).collect()))])
}

/// Unlock flags, 2 bits each in memory: 0 unknown, 1 false, 2 true. The game's unlock
/// expressions (0x28E590) fail on unknown flags, so a new player needs every flag defined:
/// the profile carries 3100 (0x808018C7 +0x383C, type 0x80800300) and 512 more (+0x5428,
/// 0x80801807), the active character
/// 2560 (0x80801714 +0x53C0, type 0x8080165B). All false = nothing done yet, which is what
/// lets the prologue (first mission) start: it requires flags 836 and 2838 to be false.
/// Account-wide overrides for scope-0 flags (master flag index, state 1 false / 2 true).
/// 836 false gates the prologue; 0x1A3 / 0x1B8 are the alternatives of an activity
/// purchase prerequisite (world transition, 0x5505C0: "unpurchased prerequisites").
const PROFILE_FLAG_OVERRIDES: &[(i64, i64)] = &[(836, 1), (0x1A3, 2), (0x1B8, 2)];

/// Flags a character past the opening story has (research: read off the director's activity
/// lists, D1_TRACE_DIRECTOR): destinations and story nodes stay hidden while these are false.
const VETERAN_FLAGS: &[i64] = &[98, 430, 434, 435, 2549, 2566, 3916, 5998];

/// The profile's override list (at most 64): the fixed overrides, then with
/// D1B_PROLOGUE_DONE=1 flag 836 true plus the veteran flags, then D1B_FLAGS_TRUE /
/// D1B_FLAGS_FALSE (comma-separated master flag indices, research).
fn profile_flag_overrides() -> Vec<(i64, i64)> {
    let env_on = |k: &str| std::env::var(k).is_ok_and(|v| v == "1");
    let list = |k: &str| -> Vec<i64> {
        std::env::var(k).unwrap_or_default().split(',').filter_map(|t| t.trim().parse().ok()).collect()
    };
    let mut ov: Vec<(i64, i64)> = PROFILE_FLAG_OVERRIDES.to_vec();
    let mut set = |flag: i64, state: i64| match ov.iter_mut().find(|(f, _)| *f == flag) {
        Some(e) => e.1 = state,
        None => ov.push((flag, state)),
    };
    if env_on("D1B_PROLOGUE_DONE") {
        set(836, 2);
        for &f in VETERAN_FLAGS {
            set(f, 2);
        }
    }
    for f in list("D1B_FLAGS_TRUE") {
        set(f, 2);
    }
    for f in list("D1B_FLAGS_FALSE") {
        set(f, 1);
    }
    ov.truncate(64);
    ov
}

/// Seconds since 1970 for the client's scheduled content: now, or D1B_SERVER_TIME (research).
pub fn server_time() -> i64 {
    std::env::var("D1B_SERVER_TIME").ok().and_then(|v| v.parse().ok()).unwrap_or_else(|| {
        std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0)
    })
}

fn unlock_flags(n: usize) -> Value {
    Value::Array((0..n).map(|_| Some(Value::Int(1))).collect())
}

/// Character summary 0x80801954 / active character 0x80801714 both start
/// {soid, {race, gender, class}, appearance}.
fn character_head(ch: &crate::account::Character) -> Value {
    use Value::*;
    let (rgc, look) = creation(ch);
    Struct(vec![Some(Int(ch.id)), Some(rgc.unwrap_or(Struct(vec![Some(Int(0)), Some(Int(0)), Some(Int(0))]))), look])
}

/// Character creation (0x1F5): store it and return its id.
pub fn create_character(req: &Request) -> i64 {
    let mut w = BitWriter::default();
    encode(&mut w, TYPE_CREATE_REQUEST, req.body.as_ref().unwrap_or(&Value::Struct(vec![])));
    let creation = hex(&w.finish());
    let first = first_character_id();
    crate::account::with(|a| {
        let id = first + a.characters.len() as i64;
        a.characters.push(crate::account::Character { id, creation, client_state: None });
        id
    })
}

pub fn account_baseline() -> FamilyUpdate {
    use Value::*;
    let account = Struct(vec![Some(Int(account_id())), Some(character_list()), None, None]);
    let mut objects = vec![Object { ty: TYPE_ACCOUNT, soid: account_id(), value: account }];
    for ch in characters() {
        objects.push(Object { ty: TYPE_CHARACTER_SUMMARY, soid: ch.id, value: character_head(&ch) });
    }
    FamilyUpdate { family: FAMILY_ACCOUNT, root: account_id(), version: crate::account::next_version(FAMILY_ACCOUNT), flags: 1, objects }
}

/// Family 4 (account profile): slot 0 0x80801803 wraps the profile 0x808018C7 {soid,
/// {character count, ids}, ..., +0x68 linked object id, ...}. The client registers it for the
/// account after sign-in and waits for its baseline (account slot ready flag, 0x586970).
pub const FAMILY_PROFILE: u32 = 4;
pub const TYPE_PROFILE: &str = "0x80801803";
/// Family 4 slot 1: the active character's full state (wrapper of 0x80801714 {soid,
/// {race, gender, class}, appearance, ...}). The profile's +0x68 names it; the account slot
/// only reports a character as selected once that object exists (0x586970 / 0x586510).
pub const TYPE_ACTIVE_CHARACTER: &str = "0x80801743";

pub fn profile_baseline() -> FamilyUpdate {
    use Value::*;
    let active = characters().last().cloned();
    let mut profile: Vec<Option<Value>> = vec![Some(Int(account_id())), Some(character_list()), None, active.as_ref().map(|c| Int(c.id))];
    profile.resize(15, None);
    profile[5] = stored_state(crate::account::with(|a| a.client_state.clone()), TYPE_ACCOUNT_CLIENT_STATE)
        .or_else(test_account_state);
    profile[10] = Some(unlock_flags(3100));
    // +0x4AC0 (0x80800FD7): {i64, {count, 64 {flag, state}}, {count, 64 {value, i32}}}:
    // overrides for flags of no storage scope (applied by 0x28BC60 case 5)
    let ov: Vec<Option<Value>> = profile_flag_overrides()
        .into_iter()
        .map(|(flag, state)| Some(Struct(vec![Some(Int(flag)), Some(Int(state))])))
        .collect();
    profile[12] = Some(Struct(vec![None, Some(Struct(vec![Some(Int(ov.len() as i64)), Some(Array(ov))])),
                                   Some(Struct(vec![Some(Int(0)), Some(Array(vec![]))]))]));
    // +0x5428 (0x80801807): {i64, 512 more flags}
    profile[14] = Some(Struct(vec![None, Some(unlock_flags(512))]));
    let profile = Struct(profile);
    let mut objects = vec![Object { ty: TYPE_PROFILE, soid: account_id(), value: Struct(vec![Some(profile)]) }];
    if let Some(ch) = active {
        let mut c = match character_head(&ch) {
            Struct(f) => f,
            _ => vec![],
        };
        c.resize(16, None);
        c[7] = stored_state(ch.client_state.clone(), TYPE_CHARACTER_CLIENT_STATE);
        // +0x3E58 (0x80801755) member 7 (+0x3E80, 0x808017B4 {present, i64 seconds}): the
        // server time the scheduled unlock flags (scope 12: expansions, events, weekly
        // rotations) are evaluated at (0x265100). Without it the client counts from 0, i.e.
        // 1970, before anything was released.
        let mut timing = vec![None; 8];
        timing[7] = Some(Struct(vec![Some(Bool(true)), Some(Int(server_time()))]));
        c[9] = Some(Struct(timing));
        // character flags; slot 673 = flag 2838, set on a new character: the prologue
        // (first mission) needs it true and flag 836 false
        let mut flags = unlock_flags(2560);
        // D1B_PROLOGUE_DONE=1 (research): the character has finished the prologue, so it is
        // not held in the new-player experience (2838 also gates joining, 0x546F20)
        let prologue_done = std::env::var("D1B_PROLOGUE_DONE").is_ok_and(|v| v == "1");
        if let Array(f) = &mut flags {
            f[673] = Some(Int(if prologue_done { 1 } else { 2 }));
        }
        c[11] = Some(flags);
        // +0x6FD0 (0x808018BB) +0x84: up to 20 {flag, state} overrides for flags kept
        // nowhere else (scope 0 in the master flag table, vtable +0x2B8; applied by
        // 0x28BC60). Flag 836 is one of those and gates the prologue.
        // 836 true once the prologue is done (with 2838 false: what finishing it leaves)
        // The same list carries the veteran flags (and D1B_FLAGS_TRUE/FALSE): the profile's
        // override list alone does not reach them.
        let mut overrides = vec![Some(Struct(vec![Some(Int(836)), Some(Int(if prologue_done { 2 } else { 1 }))]))];
        for (flag, state) in profile_flag_overrides() {
            if flag != 836 && !PROFILE_FLAG_OVERRIDES.iter().any(|&(f, _)| f == flag) && overrides.len() < 20 {
                overrides.push(Some(Struct(vec![Some(Int(flag)), Some(Int(state))])));
            }
        }
        let mut st = vec![None; 6];
        st[5] = Some(Struct(vec![Some(Int(overrides.len() as i64)), Some(Array(overrides))]));
        c[15] = Some(Struct(st));
        objects.push(Object { ty: TYPE_ACTIVE_CHARACTER, soid: ch.id, value: Struct(vec![Some(Struct(c))]) });
    }
    FamilyUpdate { family: FAMILY_PROFILE, root: account_id(), version: crate::account::next_version(FAMILY_PROFILE), flags: 1, objects }
}

/// Family 0 (peer view of an account, rooted at the account id): what every peer in an
/// activity subscribes to for each member (c_investment_peer_subscription_manager, 0x57D1D0,
/// fed by the roster the simulation host enqueues, 0x58B570). Slot 0 0x80801921 {soid,
/// character id @8, ...}; slot 1 0x808017FD {soid, {race, gender, class}, appearance,
/// loadout 0x80801855 @0x30, ...}. The character data cache (0x58D940 / 0x58DC90) resolves
/// account -> character through them and builds the player configuration (body, gear;
/// 0x911850 -> player data +0x1660) the spawner needs: without it the player gets no body.
pub const FAMILY_PEER: u32 = 0;
pub const TYPE_PEER_ACCOUNT: &str = "0x80801921";
pub const TYPE_PEER_CHARACTER: &str = "0x808017fd";

pub fn peer_baseline() -> FamilyUpdate {
    use Value::*;
    let active = characters().last().cloned();
    let mut objects = vec![Object {
        ty: TYPE_PEER_ACCOUNT,
        soid: account_id(),
        value: Struct(vec![Some(Int(account_id())), active.as_ref().map(|c| Int(c.id))]),
    }];
    if let Some(ch) = active {
        objects.push(Object { ty: TYPE_PEER_CHARACTER, soid: ch.id, value: character_head(&ch) });
    }
    FamilyUpdate { family: FAMILY_PEER, root: account_id(), version: crate::account::next_version(FAMILY_PEER), flags: 1, objects }
}

/// Baseline of a family the client subscribes to (BAP message 12). Families we hold no
/// objects for get an empty baseline (the client logs "object-count of zero" but marks the
/// family live, which is what the peer-subscription check waits for).
pub fn family_baseline(family: u32, root: i64) -> Option<FamilyUpdate> {
    // Another player's account root (a friend subscribing): build it as that player.
    let off = root.wrapping_sub(ACCOUNT_ID_BASE);
    if off != crate::account::id_offset() && off & 0xFFFF_FFFF == 0 && off >= 0 {
        let players = crate::account::players();
        if let Some(name) = players.get((off >> 32) as usize) {
            let name = name.clone();
            return crate::account::as_player(&name, || own_family_baseline(family, root));
        }
    }
    own_family_baseline(family, root)
}

/// Family 7: the player's network session (what a friend's join manager reads after the
/// roster's "join"). Slot 0 0x8080192C {soid, id of the slot-1 object}; slot 1 0x80801899 {soid, 0x808018FE
/// {bytes[<=128] (0x808043BC: u8 length, bytes) = the 0x4E-byte fireteam session data (the
/// PSN session-data / presence blob: host address, id, security key), u64 network
/// compatibility value (0x5001; the joiner compares it with its own, 0x78C210)}}.
pub const FAMILY_SESSION: u32 = 7;

pub fn session_baseline() -> FamilyUpdate {
    use Value::*;
    // the 0x4E-byte session data (0x2E94F0 copies it only at exactly that length)
    let sid = crate::npwebapi::session_data(&crate::account::current()).filter(|d| d.len() == 0x4E);
    let net_version = crate::account::with(|a| a.net_version).unwrap_or(0x5001) as i64;
    // slot 0 {soid, id of the slot-1 session object} (0x57AA70 follows it; 0 = no session)
    let session_soid = account_id() + 7;
    let mut objects = vec![Object {
        ty: "0x8080192c",
        soid: account_id(),
        value: Struct(vec![Some(Int(account_id())), Some(Int(if sid.is_some() { session_soid } else { 0 }))]),
    }];
    if let Some(sid) = sid {
        let bytes: Vec<Option<Value>> = sid.iter().map(|&b| Some(Int(b as i64))).collect();
        let text = Struct(vec![Some(Int(bytes.len() as i64)), Some(Array(bytes))]);
        objects.push(Object {
            ty: "0x80801899",
            soid: session_soid,
            value: Struct(vec![Some(Int(session_soid)), Some(Struct(vec![Some(text), Some(Int(net_version))]))]),
        });
    }
    FamilyUpdate { family: FAMILY_SESSION, root: account_id(), version: crate::account::next_version(FAMILY_SESSION), flags: 1, objects }
}

/// Family 2: the player's activity status (read by a friend's join manager, 0x580840 /
/// 0x57A970). Slot 0 0x808018B7 {soid, id of the slot-1 object, ...}; slot 1 0x80801810
/// {u64, i16 @8, i16 @10 (activity indices the join checks when set), i8, 0x808016F8 @16,
/// 0x808018DB @36 (fireteam limits and privacy)}. For now both indices are -1 (unknown), which
/// the join check skips, and the fireteam is open with room for three.
pub const FAMILY_STATUS: u32 = 2;

pub fn status_baseline() -> FamilyUpdate {
    use Value::*;
    let status_soid = account_id() + 2;
    let objects = vec![
        Object { ty: "0x808018b7", soid: account_id(), value: Struct(vec![Some(Int(account_id())), Some(Int(status_soid))]) },
        // +36 0x808018DB.+0 0x808018E5 {max fireteam size, max size in an activity with a
        // limit, privacy (0 open, 1 friends, 2 invite, 3 closed), flags}: what a friend's join
        // check (0x955EF0) compares with its fireteam (bits 0x4/0x10000/0x1000/0x2000/0x8..).
        Object {
            ty: "0x80801810",
            soid: status_soid,
            value: Struct(vec![
                Some(Int(status_soid)),
                Some(Int(-1)),
                Some(Int(-1)),
                None,
                None,
                Some(Struct(vec![Some(Struct(vec![Some(Int(3)), Some(Int(3)), Some(Int(0)), Some(Int(0))])), None, None])),
            ]),
        },
    ];
    FamilyUpdate { family: FAMILY_STATUS, root: account_id(), version: crate::account::next_version(FAMILY_STATUS), flags: 1, objects }
}

fn own_family_baseline(family: u32, root: i64) -> Option<FamilyUpdate> {
    Some(match family {
        FAMILY_STATUS if root == account_id() => status_baseline(),
        FAMILY_SESSION if root == account_id() => session_baseline(),
        FAMILY_ACCOUNT if root == account_id() => account_baseline(),
        FAMILY_PROFILE if root == account_id() => profile_baseline(),
        FAMILY_PEER if root == account_id() => peer_baseline(),
        _ => FamilyUpdate { family, root, version: crate::account::next_version(family), flags: 1, objects: vec![] },
    })
}

/// Family-5 root object id: the client pre-registers that family with this soid and binds
/// the 0x1F7 response's last struct to it (0x586A10 -> 0x56D110).
pub const FAMILY5_ROOT_SOID: i64 = i64::MAX;
/// Account id returned by investment sign-in (0x1F7 response +8); the client keeps it in its
/// account slot (0x586A10) and needs it non-zero.
pub const ACCOUNT_ID_BASE: i64 = 0x4D31_0000_0000_0001;
/// The current player's account id (slot n: base + n << 32).
pub fn account_id() -> i64 {
    ACCOUNT_ID_BASE + crate::account::id_offset()
}

/// Build the response payload for a world server request (None: no response). Every
/// request needs an answer, in order: the client matches a response only against the oldest
/// outstanding request of each send queue (0xB30960), so one unanswered message blocks the
/// rest of its queue.
pub fn respond(req: &Request) -> Option<Vec<u8>> {
    use Value::*;
    Some(match req.id {
        // investment sign-in: {status {i8, i32}, i64, i32, i32, family-5 root object}
        0x1f7 => response(0x1f7, &Struct(vec![None, Some(Int(account_id())), Some(Int(0)), Some(Int(0)),
                                               Some(Struct(vec![Some(Int(FAMILY5_ROOT_SOID))]))])),
        // subscribe to a family {family type, root soid}: status + the family's baseline
        0xce => {
            let family = match &req.body {
                Some(Struct(f)) => f.first().cloned().flatten().map(|v| v.int()).unwrap_or(-1),
                _ => -1,
            };
            let update = match family as u32 {
                FAMILY_ACCOUNT => Some(queuez_update(&[account_baseline()])),
                _ => None,
            };
            response_with_extra(0xce, &Struct(vec![]), update.as_deref())
        }
        // {status, family-5 root object}: same binding as sign-in
        // character creation: {status, new character id}; the caller then pushes the
        // account and profile families with the new character
        0x1f5 => {
            let id = create_character(req);
            response(0x1f5, &Struct(vec![None, Some(Int(id))]))
        }
        // the client's own state, reported every few seconds: account (0x2BD: seen /
        // acknowledged bits such as dismissed promotions, settings) and active character
        // (0x2BE). The profile carries it back (members 5 / 7); without that the client
        // reverts to what the server has, e.g. the Destiny 2 pre-order screen comes back
        // right after every dismissal.
        0x2bd | 0x2be => {
            let state = match &req.body {
                Some(Struct(f)) => f.first().cloned().flatten(),
                _ => None,
            };
            // the character's state changes all the time (it holds where the player is), so
            // only an account state change is pushed back right away
            if state.map_or(false, |v| store_client_state(req.id, &v)) && req.id == 0x2bd {
                PROFILE_DIRTY.store(true, std::sync::atomic::Ordering::Relaxed);
            }
            empty_response(req.id)
        }
        0xcd => response(0xcd, &Struct(vec![None, Some(Struct(vec![Some(Int(FAMILY5_ROOT_SOID))]))])),
        id => empty_response(id),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn create_character_roundtrip() {
        crate::account::init(None);
        // request: race 1, gender 0, class 2 and a default appearance
        let body = Value::Struct(vec![Some(Value::Struct(vec![Some(Value::Int(1)), Some(Value::Int(0)), Some(Value::Int(2))]))]);
        let mut w = BitWriter::default();
        w.bits(0x1f5, 16);
        encode(&mut w, TYPE_CREATE_REQUEST, &body);
        w.bit(false);
        let req = parse_request(&w.finish());
        assert_eq!(req.id, 0x1f5);
        let resp = respond(&req).unwrap();
        let mut r = BitReader::new(&resp);
        assert_eq!(r.bits(16), 0x1f5);
        let v = decode(&mut r, &schema().messages["0x1f5"].res);
        assert!(show(&v).contains(&first_character_id().to_string()), "{}", show(&v));
        let ch = &crate::account::characters()[0];
        assert!(show(&character_head(ch)).starts_with(&format!("{{{}, {{1, 0, 2}}", first_character_id())));
        // the pushes encode
        assert!(!queuez_update(&[account_baseline(), profile_baseline()]).is_empty());
    }

    #[test]
    fn request_1f7_roundtrip() {
        // captured from the client: 0x1F7 with its account name and id
        let hex = "01f744314e6174697665477561726469616e000000000000000000000000000000000000000044063b76cfed0c9500";
        let bytes: Vec<u8> = (0..hex.len()).step_by(2).map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap()).collect();
        let req = parse_request(&bytes);
        assert_eq!(req.id, 0x1f7);
        let body = req.body.unwrap();
        assert!(show(&body).contains("D1NativeGuardian"), "{}", show(&body));
        let mut w = BitWriter::default();
        w.bits(0x1f7, 16);
        encode(&mut w, &schema().messages["0x1f7"].req, &body);
        w.bit(false);
        assert_eq!(w.finish(), bytes);
    }
}
