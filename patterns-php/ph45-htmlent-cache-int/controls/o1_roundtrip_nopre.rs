// ph45 control -- THE MUST-FIRE HALF of `o1_roundtrip.rs`. The same two lines
// with the precondition deleted. It MUST fail; read that file's header.

use vstd::prelude::*;
verus!{
fn store_and_back(idx: usize) -> (r: usize)
    ensures r == idx,
{
    let cache: i32 = idx as i32;
    let back: usize = cache as usize;
    back
}
fn main() {}
}
