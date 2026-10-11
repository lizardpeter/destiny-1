// Exact Fortnite source AES key parsing contract used by production extract.rs.
pub fn parse_aes_key(hex:&str)->Result<[u8;32],String>{
    let hex=hex.strip_prefix("0x").unwrap_or(hex);
    if hex.len()!=64||!hex.bytes().all(|c|c.is_ascii_hexdigit()){
        return Err("Fortnite 5.41 source AES key must contain 64 hexadecimal digits".into());
    }
    let mut bytes=[0u8;32];
    for i in 0..32{
        bytes[i]=u8::from_str_radix(&hex[i*2..i*2+2],16)
            .map_err(|_|"invalid Fortnite 5.41 AES hexadecimal key")?;
    }
    Ok(bytes)
}
