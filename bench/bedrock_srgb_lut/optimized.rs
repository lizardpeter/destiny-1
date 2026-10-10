use std::sync::OnceLock;
fn linear_byte_to_srgb_table() -> &'static [u8; 256] {
    static TABLE: OnceLock<[u8; 256]> = OnceLock::new();
    TABLE.get_or_init(|| std::array::from_fn(|index| {
        let value = (index as f32) / 255.0;
        let encoded = if value <= 0.0031308 {
            value * 12.92
        } else {
            1.055 * value.powf(1.0 / 2.4) - 0.055
        };
        (encoded * 255.0).round().clamp(0.0, 255.0) as u8
    }))
}

#[inline]
fn linear_byte_to_srgb(linear: u8) -> u8 {
    linear_byte_to_srgb_table()[usize::from(linear)]
}

pub fn convert(input: &[u8], output: &mut [u8]) {
    let emissive_table = linear_byte_to_srgb_table();
    for (dst, value) in output.iter_mut().zip(input) {
        *dst = emissive_table[usize::from(*value)];
    }
}
pub fn get_single(value:u8)->u8{linear_byte_to_srgb(value)}
