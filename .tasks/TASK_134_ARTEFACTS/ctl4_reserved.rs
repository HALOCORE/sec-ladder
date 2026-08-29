// CONTROL 4: a Vec with capacity RESERVED IN ADVANCE, so the `push` provably
// cannot reallocate and the C bug cannot occur.  Does safe Rust still refuse?
#![forbid(unsafe_code)]
fn main() {
    let mut v: Vec<u8> = Vec::with_capacity(64);
    v.push(1);
    let r = &v[0];
    v.push(2);            // capacity 64, len 1 -> cannot reallocate
    println!("{} {}", *r, v.len());
}
