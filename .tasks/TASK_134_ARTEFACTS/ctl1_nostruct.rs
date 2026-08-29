// CONTROL 1 for the E0502 claim: NO growable buffer, NO allocator, NO Vec.
// A plain struct with one integer field.  If this also prints E0502, then the
// diagnostic p25's safe rung produces is generic borrowck, not a fact about
// `realloc` or about `Vec`.
#![forbid(unsafe_code)]
struct S { v: u32 }
impl S { fn bump(&mut self) { self.v += 1; } }
fn main() {
    let mut s = S { v: 1 };
    let r = &s.v;         // shared borrow
    s.bump();             // mutable borrow while `r` is live
    println!("{}", *r);
}
