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
        k => panic!("investment kind {k} not supported for encoding"),
    }
}

fn decode_scalar(r: &mut BitReader, m: &Member) -> Value {
    match m.kind {
        2 => Value::Bool(r.bit()),
        11 => Value::Float(f32::from_bits(r.bits(32) as u32)),
        3..=10 => {
            let raw = r.bits(m.bits) as i64;
            let v = raw.wrapping_sub(m.bias as i64);
            // sign-extend to the field width (8/16/32/64 by kind)
            let w = match m.kind { 3 | 7 => 8, 4 | 8 => 16, 5 | 9 => 32, _ => 64 };
            Value::Int(if w == 64 { v } else { ((v << (64 - w)) >> (64 - w)) as i64 })
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

pub fn account_baseline() -> FamilyUpdate {
    use Value::*;
    let account = Struct(vec![Some(Int(ACCOUNT_ID)), Some(Struct(vec![Some(Int(0)), Some(Array(vec![]))])), None, None]);
    FamilyUpdate {
        family: FAMILY_ACCOUNT,
        root: ACCOUNT_ID,
        version: 1,
        flags: 1,
        objects: vec![Object { ty: TYPE_ACCOUNT, soid: ACCOUNT_ID, value: account }],
    }
}

/// Family 4 (account profile): slot 0 0x80801803 wraps the profile 0x808018C7 {soid,
/// {character count, ids}, ..., +0x68 linked object id, ...}. The client registers it for the
/// account after sign-in and waits for its baseline (account slot ready flag, 0x586970).
pub const FAMILY_PROFILE: u32 = 4;
pub const TYPE_PROFILE: &str = "0x80801803";

pub fn profile_baseline() -> FamilyUpdate {
    use Value::*;
    let profile = Struct(vec![Some(Int(ACCOUNT_ID)), Some(Struct(vec![Some(Int(0)), Some(Array(vec![]))]))]);
    FamilyUpdate {
        family: FAMILY_PROFILE,
        root: ACCOUNT_ID,
        version: 1,
        flags: 1,
        objects: vec![Object { ty: TYPE_PROFILE, soid: ACCOUNT_ID, value: Struct(vec![Some(profile)]) }],
    }
}

/// Family-5 root object id: the client pre-registers that family with this soid and binds
/// the 0x1F7 response's last struct to it (0x586A10 -> 0x56D110).
pub const FAMILY5_ROOT_SOID: i64 = i64::MAX;
/// Account id returned by investment sign-in (0x1F7 response +8); the client keeps it in its
/// account slot (0x586A10) and needs it non-zero.
pub const ACCOUNT_ID: i64 = 0x4D31_0000_0000_0001;

/// Build the response payload for a world server request.
pub fn respond(req: &Request) -> Vec<u8> {
    use Value::*;
    match req.id {
        // investment sign-in: {status {i8, i32}, i64, i32, i32, family-5 root object}
        0x1f7 => response(0x1f7, &Struct(vec![None, Some(Int(ACCOUNT_ID)), Some(Int(0)), Some(Int(0)),
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
        id => empty_response(id),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
