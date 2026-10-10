//! SMG JMap/BCSV table reader.
//! Field lookup uses the exact SMG 0x1f rolling hash.

#[derive(Clone, Debug)]
pub struct BcsvField {
    pub name_hash: u32,
    pub bitmask: u32,
    pub record_offset: u16,
    pub shift: u8,
    pub field_type: u8,
}

#[derive(Clone, Debug, PartialEq)]
pub enum BcsvValue {
    Int(i32),
    Float(f32),
    Text(String),
}

#[derive(Clone, Debug)]
pub struct Bcsv {
    pub fields: Vec<BcsvField>,
    pub records: Vec<Vec<BcsvValue>>,
}

impl Bcsv {
    pub fn parse(bytes: &[u8]) -> Result<Self, String> {
        if bytes.len() < 0x10 {
            return Err("BCSV header is truncated".to_owned());
        }
        let record_count = be32(bytes, 0)? as usize;
        let field_count = be32(bytes, 4)? as usize;
        let record_off = be32(bytes, 8)? as usize;
        let record_size = be32(bytes, 0x0c)? as usize;
        let fields_end = 0x10usize.checked_add(field_count.checked_mul(0x0c).ok_or("BCSV field overflow")?)
            .ok_or("BCSV field overflow")?;
        if fields_end > bytes.len() || record_off < fields_end {
            return Err("BCSV field table is invalid".to_owned());
        }
        let record_bytes = record_count.checked_mul(record_size).ok_or("BCSV record overflow")?;
        let string_table = record_off.checked_add(record_bytes).ok_or("BCSV string-table overflow")?;
        if string_table > bytes.len() {
            return Err("BCSV record table is truncated".to_owned());
        }

        let mut fields = Vec::with_capacity(field_count);
        for i in 0..field_count {
            let off = 0x10 + i * 0x0c;
            fields.push(BcsvField {
                name_hash: be32(bytes, off)?,
                bitmask: be32(bytes, off + 4)?,
                record_offset: be16(bytes, off + 8)?,
                shift: *bytes.get(off + 0x0a).ok_or("BCSV shift missing")?,
                field_type: *bytes.get(off + 0x0b).ok_or("BCSV type missing")?,
            });
        }

        let mut records = Vec::with_capacity(record_count);
        for row in 0..record_count {
            let base = record_off + row * record_size;
            let mut values = Vec::with_capacity(field_count);
            for field in &fields {
                let off = base.checked_add(field.record_offset as usize).ok_or("BCSV field offset overflow")?;
                let value = match field.field_type {
                    0 => {
                        let raw = be32(bytes, off)?;
                        let masked = (raw & field.bitmask) >> field.shift;
                        BcsvValue::Int(masked as i32)
                    }
                    1 => BcsvValue::Text(fixed_c_string(bytes, off, 0x20)?),
                    2 => BcsvValue::Float(f32::from_bits(be32(bytes, off)?)),
                    4 => {
                        let raw = be16(bytes, off)? as u32;
                        let masked = (raw & field.bitmask) >> field.shift;
                        BcsvValue::Int((masked as i16) as i32)
                    }
                    5 => {
                        let raw = *bytes.get(off).ok_or("BCSV s8 out of range")? as u32;
                        let masked = (raw & field.bitmask) >> field.shift;
                        BcsvValue::Int((masked as i8) as i32)
                    }
                    6 => {
                        let rel = be32(bytes, off)? as usize;
                        let str_off = string_table.checked_add(rel).ok_or("BCSV string offset overflow")?;
                        BcsvValue::Text(c_string_lossy(bytes, str_off)?)
                    }
                    ty => return Err(format!("unsupported BCSV field type {ty}")),
                };
                values.push(value);
            }
            records.push(values);
        }
        Ok(Self { fields, records })
    }

    pub fn field_index(&self, name: &str) -> Option<usize> {
        let hash = bcsv_hash_smg(name);
        self.fields.iter().position(|f| f.name_hash == hash)
    }

    pub fn value(&self, row: usize, name: &str) -> Option<&BcsvValue> {
        let col = self.field_index(name)?;
        self.records.get(row)?.get(col)
    }

    pub fn text(&self, row: usize, name: &str) -> Option<&str> {
        match self.value(row, name)? {
            BcsvValue::Text(v) => Some(v),
            _ => None,
        }
    }

    pub fn number(&self, row: usize, name: &str) -> Option<f32> {
        match self.value(row, name)? {
            BcsvValue::Float(v) => Some(*v),
            BcsvValue::Int(v) => Some(*v as f32),
            _ => None,
        }
    }

    pub fn int(&self, row: usize, name: &str) -> Option<i32> {
        match self.value(row, name)? {
            BcsvValue::Int(v) => Some(*v),
            _ => None,
        }
    }
}

pub fn bcsv_hash_smg(name: &str) -> u32 {
    name.bytes().fold(0u32, |hash, b| hash.wrapping_mul(0x1f).wrapping_add(b as u32))
}

fn be16(bytes: &[u8], off: usize) -> Result<u16, String> {
    let s = bytes.get(off..off + 2).ok_or("BCSV u16 out of range")?;
    Ok(u16::from_be_bytes(s.try_into().unwrap()))
}
fn be32(bytes: &[u8], off: usize) -> Result<u32, String> {
    let s = bytes.get(off..off + 4).ok_or("BCSV u32 out of range")?;
    Ok(u32::from_be_bytes(s.try_into().unwrap()))
}
fn c_string_lossy(bytes: &[u8], off: usize) -> Result<String, String> {
    if off >= bytes.len() { return Err("BCSV string out of range".to_owned()); }
    let len = bytes[off..].iter().position(|&b| b == 0).unwrap_or(bytes.len() - off);
    Ok(String::from_utf8_lossy(&bytes[off..off + len]).into_owned())
}
fn fixed_c_string(bytes: &[u8], off: usize, max: usize) -> Result<String, String> {
    let end = off.checked_add(max).ok_or("BCSV fixed string overflow")?.min(bytes.len());
    if off >= end { return Err("BCSV fixed string out of range".to_owned()); }
    let len = bytes[off..end].iter().position(|&b| b == 0).unwrap_or(end - off);
    Ok(String::from_utf8_lossy(&bytes[off..off + len]).into_owned())
}

