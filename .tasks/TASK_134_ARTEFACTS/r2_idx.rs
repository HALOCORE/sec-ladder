// p25 R2 candidate C: safe Rust, MARK saves an INDEX.  The index port.
#![forbid(unsafe_code)]
fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let mut v: Vec<u8> = Vec::new();
    let mut acc: u64 = 0;
    if len < 4 { return 0; }
    let nops = u32::from_le_bytes([buf[off], buf[off+1], buf[off+2], buf[off+3]]) as u64;
    let mut mark: Option<usize> = None;
    let mut p = 4usize;
    for _ in 0..nops {
        if len - p < 2 { break; }
        let (c, a) = (buf[off+p], buf[off+p+1]); p += 2;
        match c & 3 {
            0 => { v.push(a); acc = acc.wrapping_mul(31).wrapping_add(a as u64); }
            1 => { if (a as usize) < v.len() { mark = Some(a as usize); acc = acc.wrapping_mul(31).wrapping_add(1); }
                   else { acc = acc.wrapping_mul(31).wrapping_add(251); } }
            _ => { match mark { Some(k) => acc = acc.wrapping_mul(31).wrapping_add(v[k] as u64),
                                None => acc = acc.wrapping_mul(31).wrapping_add(251) } }
        }
    }
    acc.wrapping_mul(31).wrapping_add(v.len() as u64)
}
fn main() { let b = [0u8; 8]; println!("{}", kernel(&b, 0, 8)); }
