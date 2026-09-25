use d1_oodle3::lzh::HuffmanModel;
use d1_oodle3::{parse_quantum_header, scan_frame, DecoderType, QuantumKind};
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
    let input_path = PathBuf::from(
        args.next()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing input"))?,
    );
    let raw_len_arg = args
        .next()
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing raw length"))?;
    if args.next().is_some() {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "too many arguments").into());
    }
    let raw_len = parse_usize(&raw_len_arg.to_string_lossy())?;
    let input = fs::read(&input_path)?;
    let spans = scan_frame(&input, raw_len)?;

    let mut models = 0usize;
    for (index, span) in spans.iter().enumerate() {
        println!(
            "Q {index:02} out={:#x} raw={:#x} in={:#x}+{:#x} v={} type={:?} shift={} kind={:?}",
            span.output_offset,
            span.raw_len,
            span.input_offset,
            span.input_len,
            span.block.version,
            span.block.decoder_type,
            span.block.offset_shift,
            span.kind
        );

        if span.block.decoder_type == DecoderType::Lzh
            && matches!(span.kind, QuantumKind::Compressed { flag1: true, .. })
        {
            let header =
                parse_quantum_header(&input[span.input_offset..], span.block, span.raw_len)?;
            let payload_start = span.input_offset + header.header_len;
            let payload_end = span.input_offset + span.input_len;
            let model = HuffmanModel::parse_lzh(&input[payload_start..payload_end])?;
            println!(
                "  LZH_MODEL used={} top={:?} min={} max={} bits={} bytes_ceil={}",
                model.used_symbols,
                model.top_symbol,
                model.min_code_len,
                model.max_code_len,
                model.consumed_bits,
                model.consumed_bits.div_ceil(8)
            );
            models += 1;
        }
    }

    println!(
        "D1_OODLE23_FRAME_GREEN quanta={} models={} bytes={}",
        spans.len(),
        models,
        input.len()
    );
    Ok(())
}
