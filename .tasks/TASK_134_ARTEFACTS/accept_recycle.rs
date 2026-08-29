// THE OTHER DIRECTION.  Does the borrow checker ACCEPT a genuinely temporal
// bug in a FLAT GROWABLE BUFFER?  `pop` ends element k's lifetime; `push`
// RECYCLES the slot for a different element; the read then gets the new
// occupant.  Use-after-recycle, in bounds, under #![forbid(unsafe_code)].
#![forbid(unsafe_code)]
fn main() {
    let mut v: Vec<u32> = vec![10, 20, 30];
    let k = v.len() - 1;              // names the element valued 30
    let ptr_before = v.as_ptr() as usize;
    v.pop();                          // element k's lifetime ENDS
    v.push(9999);                     // slot k is RECYCLED
    println!("read v[{}] = {} (expected 30, the element that was marked)", k, v[k]);
    println!("buffer moved: {}", (v.as_ptr() as usize) != ptr_before);
    // and the capacity/growth path, same shape:
    let mut w: Vec<u32> = Vec::with_capacity(2);
    w.push(1); w.push(2);
    let j = 1usize;
    w.pop();
    w.push(7777);                     // reallocation NOT needed: cap is 2
    println!("read w[{}] = {} (expected 2)", j, w[j]);
}
