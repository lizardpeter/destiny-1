fn linear_byte_to_srgb(linear: u8) -> u8 {
    let value = f32::from(linear) / 255.0;
    let encoded = if value <= 0.0031308 {
        value * 12.92
    } else {
        1.055 * value.powf(1.0 / 2.4) - 0.055
    };
    (encoded * 255.0).round().clamp(0.0, 255.0) as u8
}

pub fn convert(input: &[u8], output: &mut [u8]) {
    for (dst, value) in output.iter_mut().zip(input) {
        *dst = linear_byte_to_srgb(*value);
    }
}
