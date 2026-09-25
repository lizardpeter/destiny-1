//! Minimal ABI-compatible surface for the Destiny 1 Oodle 2.3 decode path.
//!
//! This is intentionally not a claim of full Oodle DLL compatibility. Unsupported
//! callback/phased-decoding modes fail closed instead of silently producing data.

use core::ffi::c_void;
use std::panic::{catch_unwind, AssertUnwindSafe};

const THREAD_PHASE_ALL: u32 = 3;

#[unsafe(no_mangle)]
pub unsafe extern "C" fn OodleLZ_Decompress(
    comp_buf: *const c_void,
    comp_len: i64,
    raw_buf: *mut c_void,
    raw_len: i64,
    _fuzz_safe: u32,
    _check_crc: u32,
    _verbosity: u32,
    _dec_buf_base: *mut c_void,
    _dec_buf_size: *mut c_void,
    callback: *mut c_void,
    _callback_user_data: *mut c_void,
    _decoder_memory: *mut c_void,
    _decoder_memory_size: *mut c_void,
    thread_phase: u32,
) -> i64 {
    let result = catch_unwind(AssertUnwindSafe(|| {
        if comp_buf.is_null()
            || raw_buf.is_null()
            || comp_len < 0
            || raw_len < 0
            || callback.is_null().not()
            || thread_phase != THREAD_PHASE_ALL
        {
            return -1;
        }

        let comp_len = usize::try_from(comp_len).map_err(|_| ())?;
        let raw_len = usize::try_from(raw_len).map_err(|_| ())?;

        let input = unsafe { core::slice::from_raw_parts(comp_buf.cast::<u8>(), comp_len) };
        let decoded = crate::lzh::decode_stream(input, raw_len).map_err(|_| ())?;
        if decoded.len() != raw_len {
            return Err(());
        }

        unsafe {
            core::ptr::copy_nonoverlapping(decoded.as_ptr(), raw_buf.cast::<u8>(), raw_len);
        }
        Ok(i64::try_from(raw_len).map_err(|_| ())?)
    }));

    match result {
        Ok(Ok(value)) => value,
        _ => -1,
    }
}

trait BoolNot {
    fn not(self) -> bool;
}

impl BoolNot for bool {
    fn not(self) -> bool {
        !self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_unsupported_thread_phase() {
        let input = [0u8; 1];
        let mut output = [0u8; 1];
        let result = unsafe {
            OodleLZ_Decompress(
                input.as_ptr().cast(),
                input.len() as i64,
                output.as_mut_ptr().cast(),
                output.len() as i64,
                0,
                0,
                0,
                core::ptr::null_mut(),
                core::ptr::null_mut(),
                core::ptr::null_mut(),
                core::ptr::null_mut(),
                core::ptr::null_mut(),
                core::ptr::null_mut(),
                1,
            )
        };
        assert_eq!(result, -1);
    }
}
