#[inline(never)]
pub fn kernel(v: &Vec<u64>, n: usize) -> u64 {
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < n { acc = acc + unsafe { *v.get_unchecked(i) }; i = i + 1; }
    acc
}
fn main() { let v: Vec<u64> = std::env::args().skip(1).filter_map(|a| a.parse().ok()).collect(); let n = v.len(); println!("{}", kernel(&v, n)); }
