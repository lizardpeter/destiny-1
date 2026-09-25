//! Minimal ABI-compatible surface for the Destiny 1 Oodle 2.3 decode path.
//!
//! This is intentionally not a claim of full Oodle DLL compatibility. Unsupported
//! callback/phased-decoding modes fail closed instead of silently producing data.

use core::ffi::c_void;

const THREAD_PHASE_ALL: u32 = 3;

/// Decode one complete Oodle 2.3 LZH stream into the caller-provided buffer.
///
/// This compatibility export implements the whole-buffer call shape used by the
/// Destiny 1 tooling. Callback and phased-decode modes that have not been
/// reproduced return -1.
///
/// # Safety
///
/// `comp_buf` must reference at least `comp_len` readable bytes and
/// `raw_buf` must reference at least `raw_len` writable bytes. The buffers
/// must remain valid for the duration of the call. Unsupported callback or
/// phased-decoding arguments fail closed.
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
    if comp_buf.is_null()
        || raw_buf.is_null()
        || comp_len < 0
        || raw_len < 0
        || !callback.is_null()
        || thread_phase != THREAD_PHASE_ALL
    {
        return -1;
    }

    let Ok(comp_len) = usize::try_from(comp_len) else {
        return -1;
    };
    let Ok(raw_len) = usize::try_from(raw_len) else {
        return -1;
    };

    let comp_start = comp_buf as usize;
    let raw_start = raw_buf as usize;
    let Some(comp_end) = comp_start.checked_add(comp_len) else {
        return -1;
    };
    let Some(raw_end) = raw_start.checked_add(raw_len) else {
        return -1;
    };
    if comp_start < raw_end && raw_start < comp_end {
        return -1;
    }

    let input = unsafe { core::slice::from_raw_parts(comp_buf.cast::<u8>(), comp_len) };
    let output = unsafe { core::slice::from_raw_parts_mut(raw_buf.cast::<u8>(), raw_len) };
    if crate::lzh::decode_stream_into(input, output).is_err() {
        return -1;
    }

    i64::try_from(raw_len).unwrap_or(-1)

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
