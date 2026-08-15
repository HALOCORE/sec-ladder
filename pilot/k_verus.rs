use vstd::prelude::*;
verus! {
#[verifier::external_body]
fn out(x: u64) { println!("{}", x); }

#[inline(never)]
pub fn kernel(v: &Vec<u64>, n: usize) -> (r: u64)
    requires n <= v.len(), n < 1000, forall|i: int| 0 <= i < n ==> v[i] < 1000,
    ensures r < 1000 * 1000,
{
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < n
        invariant i <= n, n <= v.len(), n < 1000, acc <= 1000 * i,
                  forall|j: int| 0 <= j < n ==> v[j] < 1000,
        decreases n - i,
    { acc = acc + v[i]; i = i + 1; }
    acc
}
#[verifier::external_body]
fn main() { let v: Vec<u64> = std::env::args().skip(1).filter_map(|a| a.parse().ok()).collect(); let n = v.len(); out(kernel(&v, n)); }
} // verus!
