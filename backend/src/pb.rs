//! Minimal protobuf wire-format writer/reader. Bungie's "schematized" messages
//! (decoder at eboot+0xA17D0, schema tables of 23-byte field records) use standard
//! protobuf encoding: varints, length-delimited bytes/strings/sub-messages.

#[derive(Default, Clone)]
pub struct Msg(Vec<u8>);

impl Msg {
    pub fn new() -> Self {
        Self(Vec::new())
    }
    fn key(&mut self, field: u32, wire: u8) {
        varint(&mut self.0, (u64::from(field) << 3) | u64::from(wire));
    }
    pub fn uint(mut self, field: u32, v: u64) -> Self {
        self.key(field, 0);
        varint(&mut self.0, v);
        self
    }
    pub fn int(self, field: u32, v: i64) -> Self {
        self.uint(field, v as u64)
    }
    pub fn bytes(mut self, field: u32, b: &[u8]) -> Self {
        self.key(field, 2);
        varint(&mut self.0, b.len() as u64);
        self.0.extend_from_slice(b);
        self
    }
    pub fn str(self, field: u32, s: &str) -> Self {
        self.bytes(field, s.as_bytes())
    }
    pub fn msg(self, field: u32, m: Msg) -> Self {
        self.bytes(field, &m.0)
    }
    pub fn fixed32(mut self, field: u32, v: u32) -> Self {
        self.key(field, 5);
        self.0.extend_from_slice(&v.to_le_bytes());
        self
    }
    pub fn into_bytes(self) -> Vec<u8> {
        self.0
    }
}

fn varint(out: &mut Vec<u8>, mut v: u64) {
    loop {
        let b = (v & 0x7f) as u8;
        v >>= 7;
        if v == 0 {
            out.push(b);
            return;
        }
        out.push(b | 0x80);
    }
}

/// One decoded field: number and value (varint / fixed / length-delimited).
#[derive(Debug, Clone)]
pub enum Val {
    Varint(u64),
    Fixed64(u64),
    Bytes(Vec<u8>),
    Fixed32(u32),
}

pub fn parse(mut b: &[u8]) -> Option<Vec<(u32, Val)>> {
    fn rv(b: &mut &[u8]) -> Option<u64> {
        let mut v = 0u64;
        for i in 0..10 {
            let (&c, rest) = b.split_first()?;
            *b = rest;
            v |= u64::from(c & 0x7f) << (7 * i);
            if c & 0x80 == 0 {
                return Some(v);
            }
        }
        None
    }
    let mut out = Vec::new();
    while !b.is_empty() {
        let key = rv(&mut b)?;
        let field = (key >> 3) as u32;
        let v = match key & 7 {
            0 => Val::Varint(rv(&mut b)?),
            1 => {
                let (x, rest) = b.split_at_checked(8)?;
                b = rest;
                Val::Fixed64(u64::from_le_bytes(x.try_into().ok()?))
            }
            2 => {
                let n = rv(&mut b)? as usize;
                let (x, rest) = b.split_at_checked(n)?;
                b = rest;
                Val::Bytes(x.to_vec())
            }
            5 => {
                let (x, rest) = b.split_at_checked(4)?;
                b = rest;
                Val::Fixed32(u32::from_le_bytes(x.try_into().ok()?))
            }
            _ => return None,
        };
        out.push((field, v));
    }
    Some(out)
}

/// Human-readable dump of a message (sub-messages are guessed and expanded).
pub fn dump(b: &[u8], indent: usize) -> String {
    let mut s = String::new();
    match parse(b) {
        None => s.push_str(&format!("{:indent$}<not protobuf: {} bytes>\n", "", b.len())),
        Some(fields) => {
            for (f, v) in fields {
                match v {
                    Val::Bytes(x) => {
                        let printable = x.iter().all(|c| (0x20..0x7f).contains(c));
                        if printable && !x.is_empty() {
                            s.push_str(&format!("{:indent$}{f}: {:?}\n", "", String::from_utf8_lossy(&x)));
                        } else if !x.is_empty() && parse(&x).is_some_and(|p| !p.is_empty()) && indent < 24 {
                            s.push_str(&format!("{:indent$}{f}: {{\n", ""));
                            s.push_str(&dump(&x, indent + 2));
                            s.push_str(&format!("{:indent$}}}\n", ""));
                        } else {
                            s.push_str(&format!("{:indent$}{f}: bytes[{}] {}\n", "", x.len(), hex(&x[..x.len().min(48)])));
                        }
                    }
                    other => s.push_str(&format!("{:indent$}{f}: {other:?}\n", "")),
                }
            }
        }
    }
    s
}

pub fn hex(b: &[u8]) -> String {
    b.iter().map(|c| format!("{c:02x}")).collect()
}
