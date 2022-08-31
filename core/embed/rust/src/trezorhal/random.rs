use super::ffi;

pub fn uniform(n: u32) -> u32 {
    unsafe { ffi::random_uniform(n) }
}

pub fn shuffle<T>(slice: &mut [T]) {
    // Fisher-Yates shuffle.
    for i in (1..slice.len()).rev() {
        let j = uniform(i as u32 + 1) as usize;
        slice.swap(i, j);
    }
}

pub fn bytes(buf: &mut [u8]) {
    unsafe { ffi::random_buffer(buf.as_mut_ptr() as _, buf.len()) };
}
