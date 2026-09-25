use oozextract::Extractor;
use std::{env, fs, io, path::PathBuf};

fn parse_usize(s: &str) -> Result<usize, Box<dyn std::error::Error>> {
    let v = s.trim();
    Ok(
        if let Some(hex) = v.strip_prefix("0x").or_else(|| v.strip_prefix("0X")) {
            usize::from_str_radix(hex, 16)?
        } else {
            v.parse()?
        },
    )
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args_os().skip(1);
    let input = PathBuf::from(
        args.next()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing input"))?,
    );
    let raw_len_os = args
        .next()
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing raw length"))?;
    let raw_len = parse_usize(&raw_len_os.to_string_lossy())?;
    let output = PathBuf::from(
        args.next()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing output"))?,
    );
    if args.next().is_some() {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "too many arguments").into());
    }

    let compressed = fs::read(input)?;
    let mut decoded = vec![0u8; raw_len];
    let written = Extractor::new().read_from_slice(&compressed, &mut decoded)?;
    if written != raw_len {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            format!("decoder wrote {written:#x}, expected {raw_len:#x}"),
        )
        .into());
    }
    fs::write(output, decoded)?;
    Ok(())
}
