// ph45 control -- OBLIGATION O1, ISOLATED, IN BOTH DIRECTIONS.
//
// `paper/invariants-166.json`'s `pointer-value-integrity` O1:
//   "a pointer must not be stored into an integer field narrower than a
//    pointer, nor otherwise round-tripped through a type that cannot represent
//    every pointer value"
//
// This file is `mbfilter_htmlent.c:161` followed by `:178`, with nothing else
// in it, and the precondition that makes the round trip lossless.
//
//     python3 ./verus_run.py patterns-php/ph45-htmlent-cache-int/controls/o1_roundtrip.rs
//     -> 2 verified, 0 errors                          (MUST verify)
//     python3 ./verus_run.py .../controls/o1_roundtrip_nopre.rs
//     -> 1 verified, 1 errors, `postcondition not satisfied`   (MUST fail)
//
// ⭐⭐ AND THE MUST-FAIL RUN CARRIES THE RESULT THIS ROW EXISTS FOR. Verus does
// not merely refuse it -- it names the two cast sites:
//
//   note: recommendation not met: value may be out of range of the target type
//     --> o1_roundtrip_nopre.rs:7:22   let cache: i32 = idx as i32;
//   note: recommendation not met: value may be out of range of the target type
//     --> o1_roundtrip_nopre.rs:8:23   let back: usize = cache as usize;
//
// gcc emits FOUR warnings for the same idiom in C, rustc emits ZERO even under
// `-D warnings`, and Verus REFUSES it and points at both casts. Three
// toolchains, three answers. `../NOTES.md` sections 10 and 11.

use vstd::prelude::*;

verus!{

fn store_and_back(idx: usize) -> (r: usize)
    requires idx < 0x8000_0000usize,
    ensures r == idx,
{
    let cache: i32 = idx as i32;      // the TRUNCATING STORE, mbfilter_htmlent.c:161
    let back: usize = cache as usize; // the CAST BACK, :178
    back
}

fn main() {}

}
