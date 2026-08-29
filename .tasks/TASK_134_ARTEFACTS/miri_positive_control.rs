// POSITIVE CONTROL: real UB that Miri MUST report. If this is silent, the
// Miri-clean result on accept_recycle.rs means nothing.
fn main() {
    let v: Vec<u32> = vec![1, 2, 3];
    let p = v.as_ptr();
    drop(v);
    let x = unsafe { *p };   // use after free
    println!("read {}", x);
}
