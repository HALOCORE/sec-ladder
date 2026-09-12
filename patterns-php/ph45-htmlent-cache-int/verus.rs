//! ph45 rung R5 -- `unsafe.rs`'s exec code with a Verus proof.
//!
//! ============================================================================
//! ⭐⭐⭐ WHAT IS PROVED HERE IS THE CORPUS INVARIANT ITSELF, AND THIS IS THE
//! FIRST ROW IN EITHER PROGRAMME WHERE THAT IS LITERALLY TRUE
//! ============================================================================
//! CRASH-123 is the only one of the corpus's 166 cases with its own invariant.
//! `paper/invariants-166.json` states `pointer-value-integrity` as
//!
//!   *"A pointer stored into a field and read back designates the same object
//!    it did when stored; no storage or conversion step on that round trip
//!    discards part of its value."*
//!
//! and gives it three obligations. Two of them are a `requires` in this file:
//!
//!   O1  *"a pointer must not be stored into an integer field narrower than a
//!        pointer, nor otherwise round-tripped through a type that cannot
//!        represent every pointer value"*
//!        -> `alloc`'s `ensures`: the index it returns is `0` or in
//!           `[BLOCK, ASZ - BLOCK]`, so `idx as i32 as usize == idx`.
//!   O2  *"a value read back out of such a field must not be converted to a
//!        pointer and dereferenced without re-establishing that it designates
//!        the original object"*
//!        -> `wf(f)`: `f.cache == 0 || (0 < f.cache && f.cache + BLOCK <= ASZ)`,
//!           which is what discharges `bget`/`bset`'s `i < ASZ` at all eleven
//!           dereference sites.
//!   O3  *"a value that is not an address returned by the allocator must not be
//!        handed to the deallocator"*
//!        -> `s_free`'s ledger. ⚠ NOT a memory-safety obligation in this
//!           representation: freeing a wrong index is a wrong ANSWER, not a
//!           wrong ACCESS, so O3 lives entirely in the VALUE postcondition.
//!
//! ⚠⚠ AND MEASURE THE VACUITY BEFORE BELIEVING ANY OF IT. `ph07` measured its
//! own by replacing the kernel body with `0u64`; this row owes the same and
//! `../NOTES.md` §11 carries the number. The short version: the memory-safety
//! half is NOT vacuous -- delete `alloc`'s range `ensures` and eleven
//! `bget`/`bset` calls stop verifying -- and the value half is what costs the
//! budget, exactly as `.memory-php/02-ladder.md` records for `ph07`.
//!
//! ============================================================================
//! THE TRUSTED BASE -- three items, and `../NOTES.md` §11 tallies them
//! ============================================================================
//!   `bget`  / `bset`  -- `get_unchecked` / `get_unchecked_mut` on `[u8; ASZ]`.
//!                        vstd ships no spec for either (grepped:
//!                        `~/tools/verus/vstd/std_specs/slice.rs` has `index`,
//!                        `index_mut`, `split_at`, `copy_from_slice` and no
//!                        `get_unchecked`), so they are `external_body` with a
//!                        `requires i < ASZ` and a whole-post-state `ensures`.
//!                        Each has a `slb_twin_*` under `--cfg slb_twin` that
//!                        is the SAFE body with the same contract, so the
//!                        contract is checked rather than asserted.
//!   `ent_table`        -- the 251-entity table. `tbl()` is UNINTERPRETED, so
//!                        the proof holds for ANY table and this item
//!                        axiomatises nothing about the contents. What pins the
//!                        contents is `controls/entity_table.py` (all six
//!                        shipped copies, byte for byte against the tarball,
//!                        with a must-fire negative) and `check.py` stage 2,
//!                        which makes every rung agree on a `u64` that depends
//!                        on the table. ⚠ It has no twin: a safe body cannot
//!                        prove `r@ == tbl()` about an uninterpreted function.

use vstd::prelude::*;
use vstd::slice::slice_subrange;

#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not to
// overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the
// window-offset bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

pub const ASZ: usize = 512;
pub const BLOCK: usize = 32;
pub const REGION: usize = 256;
pub const NBLK: usize = 16;
pub const REQ: usize = 17;
pub const HEAD: usize = 8;
pub const HTML_ENC_BUFFER_SIZE: i32 = 16;

pub struct Ent {
    pub name: &'static [u8],
    pub code: i32,
}

/// ⚠ UNINTERPRETED. The proof is valid for any 251-entry table; what pins the
/// real one is `controls/entity_table.py` and the gate's cross-rung checksum.
pub uninterp spec fn tbl() -> Seq<Ent>;

/// ⚠ TRUSTED #3. See the header.
#[verifier::external_body]
fn ent_table() -> (r: &'static [Ent])
    ensures
        r@ == tbl(),
{
    &[
        Ent { name: b"quot", code: 34 },
        Ent { name: b"amp", code: 38 },
        Ent { name: b"lt", code: 60 },
        Ent { name: b"gt", code: 62 },
        Ent { name: b"nbsp", code: 160 },
        Ent { name: b"iexcl", code: 161 },
        Ent { name: b"cent", code: 162 },
        Ent { name: b"pound", code: 163 },
        Ent { name: b"curren", code: 164 },
        Ent { name: b"yen", code: 165 },
        Ent { name: b"brvbar", code: 166 },
        Ent { name: b"sect", code: 167 },
        Ent { name: b"uml", code: 168 },
        Ent { name: b"copy", code: 169 },
        Ent { name: b"ordf", code: 170 },
        Ent { name: b"laquo", code: 171 },
        Ent { name: b"not", code: 172 },
        Ent { name: b"shy", code: 173 },
        Ent { name: b"reg", code: 174 },
        Ent { name: b"macr", code: 175 },
        Ent { name: b"deg", code: 176 },
        Ent { name: b"plusmn", code: 177 },
        Ent { name: b"sup2", code: 178 },
        Ent { name: b"sup3", code: 179 },
        Ent { name: b"acute", code: 180 },
        Ent { name: b"micro", code: 181 },
        Ent { name: b"para", code: 182 },
        Ent { name: b"middot", code: 183 },
        Ent { name: b"cedil", code: 184 },
        Ent { name: b"sup1", code: 185 },
        Ent { name: b"ordm", code: 186 },
        Ent { name: b"raquo", code: 187 },
        Ent { name: b"frac14", code: 188 },
        Ent { name: b"frac12", code: 189 },
        Ent { name: b"frac34", code: 190 },
        Ent { name: b"iquest", code: 191 },
        Ent { name: b"Agrave", code: 192 },
        Ent { name: b"Aacute", code: 193 },
        Ent { name: b"Acirc", code: 194 },
        Ent { name: b"Atilde", code: 195 },
        Ent { name: b"Auml", code: 196 },
        Ent { name: b"Aring", code: 197 },
        Ent { name: b"AElig", code: 198 },
        Ent { name: b"Ccedil", code: 199 },
        Ent { name: b"Egrave", code: 200 },
        Ent { name: b"Eacute", code: 201 },
        Ent { name: b"Ecirc", code: 202 },
        Ent { name: b"Euml", code: 203 },
        Ent { name: b"Igrave", code: 204 },
        Ent { name: b"Iacute", code: 205 },
        Ent { name: b"Icirc", code: 206 },
        Ent { name: b"Iuml", code: 207 },
        Ent { name: b"ETH", code: 208 },
        Ent { name: b"Ntilde", code: 209 },
        Ent { name: b"Ograve", code: 210 },
        Ent { name: b"Oacute", code: 211 },
        Ent { name: b"Ocirc", code: 212 },
        Ent { name: b"Otilde", code: 213 },
        Ent { name: b"Ouml", code: 214 },
        Ent { name: b"times", code: 215 },
        Ent { name: b"Oslash", code: 216 },
        Ent { name: b"Ugrave", code: 217 },
        Ent { name: b"Uacute", code: 218 },
        Ent { name: b"Ucirc", code: 219 },
        Ent { name: b"Uuml", code: 220 },
        Ent { name: b"Yacute", code: 221 },
        Ent { name: b"THORN", code: 222 },
        Ent { name: b"szlig", code: 223 },
        Ent { name: b"agrave", code: 224 },
        Ent { name: b"aacute", code: 225 },
        Ent { name: b"acirc", code: 226 },
        Ent { name: b"atilde", code: 227 },
        Ent { name: b"auml", code: 228 },
        Ent { name: b"aring", code: 229 },
        Ent { name: b"aelig", code: 230 },
        Ent { name: b"ccedil", code: 231 },
        Ent { name: b"egrave", code: 232 },
        Ent { name: b"eacute", code: 233 },
        Ent { name: b"ecirc", code: 234 },
        Ent { name: b"euml", code: 235 },
        Ent { name: b"igrave", code: 236 },
        Ent { name: b"iacute", code: 237 },
        Ent { name: b"icirc", code: 238 },
        Ent { name: b"iuml", code: 239 },
        Ent { name: b"eth", code: 240 },
        Ent { name: b"ntilde", code: 241 },
        Ent { name: b"ograve", code: 242 },
        Ent { name: b"oacute", code: 243 },
        Ent { name: b"ocirc", code: 244 },
        Ent { name: b"otilde", code: 245 },
        Ent { name: b"ouml", code: 246 },
        Ent { name: b"divide", code: 247 },
        Ent { name: b"oslash", code: 248 },
        Ent { name: b"ugrave", code: 249 },
        Ent { name: b"uacute", code: 250 },
        Ent { name: b"ucirc", code: 251 },
        Ent { name: b"uuml", code: 252 },
        Ent { name: b"yacute", code: 253 },
        Ent { name: b"thorn", code: 254 },
        Ent { name: b"yuml", code: 255 },
        Ent { name: b"OElig", code: 338 },
        Ent { name: b"oelig", code: 339 },
        Ent { name: b"Scaron", code: 352 },
        Ent { name: b"scaron", code: 353 },
        Ent { name: b"Yuml", code: 376 },
        Ent { name: b"fnof", code: 402 },
        Ent { name: b"circ", code: 710 },
        Ent { name: b"tilde", code: 732 },
        Ent { name: b"Alpha", code: 913 },
        Ent { name: b"Beta", code: 914 },
        Ent { name: b"Gamma", code: 915 },
        Ent { name: b"Delta", code: 916 },
        Ent { name: b"Epsilon", code: 917 },
        Ent { name: b"Zeta", code: 918 },
        Ent { name: b"Eta", code: 919 },
        Ent { name: b"Theta", code: 920 },
        Ent { name: b"Iota", code: 921 },
        Ent { name: b"Kappa", code: 922 },
        Ent { name: b"Lambda", code: 923 },
        Ent { name: b"Mu", code: 924 },
        Ent { name: b"Nu", code: 925 },
        Ent { name: b"Xi", code: 926 },
        Ent { name: b"Omicron", code: 927 },
        Ent { name: b"Pi", code: 928 },
        Ent { name: b"Rho", code: 929 },
        Ent { name: b"Sigma", code: 931 },
        Ent { name: b"Tau", code: 932 },
        Ent { name: b"Upsilon", code: 933 },
        Ent { name: b"Phi", code: 934 },
        Ent { name: b"Chi", code: 935 },
        Ent { name: b"Psi", code: 936 },
        Ent { name: b"Omega", code: 937 },
        Ent { name: b"beta", code: 946 },
        Ent { name: b"gamma", code: 947 },
        Ent { name: b"delta", code: 948 },
        Ent { name: b"epsilon", code: 949 },
        Ent { name: b"zeta", code: 950 },
        Ent { name: b"eta", code: 951 },
        Ent { name: b"theta", code: 952 },
        Ent { name: b"iota", code: 953 },
        Ent { name: b"kappa", code: 954 },
        Ent { name: b"lambda", code: 955 },
        Ent { name: b"mu", code: 956 },
        Ent { name: b"nu", code: 957 },
        Ent { name: b"xi", code: 958 },
        Ent { name: b"omicron", code: 959 },
        Ent { name: b"pi", code: 960 },
        Ent { name: b"rho", code: 961 },
        Ent { name: b"sigmaf", code: 962 },
        Ent { name: b"sigma", code: 963 },
        Ent { name: b"tau", code: 964 },
        Ent { name: b"upsilon", code: 965 },
        Ent { name: b"phi", code: 966 },
        Ent { name: b"chi", code: 967 },
        Ent { name: b"psi", code: 968 },
        Ent { name: b"omega", code: 969 },
        Ent { name: b"thetasym", code: 977 },
        Ent { name: b"upsih", code: 978 },
        Ent { name: b"piv", code: 982 },
        Ent { name: b"ensp", code: 8194 },
        Ent { name: b"emsp", code: 8195 },
        Ent { name: b"thinsp", code: 8201 },
        Ent { name: b"zwnj", code: 8204 },
        Ent { name: b"zwj", code: 8205 },
        Ent { name: b"lrm", code: 8206 },
        Ent { name: b"rlm", code: 8207 },
        Ent { name: b"ndash", code: 8211 },
        Ent { name: b"mdash", code: 8212 },
        Ent { name: b"lsquo", code: 8216 },
        Ent { name: b"rsquo", code: 8217 },
        Ent { name: b"sbquo", code: 8218 },
        Ent { name: b"ldquo", code: 8220 },
        Ent { name: b"rdquo", code: 8221 },
        Ent { name: b"bdquo", code: 8222 },
        Ent { name: b"dagger", code: 8224 },
        Ent { name: b"Dagger", code: 8225 },
        Ent { name: b"bull", code: 8226 },
        Ent { name: b"hellip", code: 8230 },
        Ent { name: b"permil", code: 8240 },
        Ent { name: b"prime", code: 8242 },
        Ent { name: b"Prime", code: 8243 },
        Ent { name: b"lsaquo", code: 8249 },
        Ent { name: b"rsaquo", code: 8250 },
        Ent { name: b"oline", code: 8254 },
        Ent { name: b"frasl", code: 8260 },
        Ent { name: b"euro", code: 8364 },
        Ent { name: b"weierp", code: 8472 },
        Ent { name: b"image", code: 8465 },
        Ent { name: b"real", code: 8476 },
        Ent { name: b"trade", code: 8482 },
        Ent { name: b"alefsym", code: 8501 },
        Ent { name: b"larr", code: 8592 },
        Ent { name: b"uarr", code: 8593 },
        Ent { name: b"rarr", code: 8594 },
        Ent { name: b"darr", code: 8595 },
        Ent { name: b"harr", code: 8596 },
        Ent { name: b"crarr", code: 8629 },
        Ent { name: b"lArr", code: 8656 },
        Ent { name: b"uArr", code: 8657 },
        Ent { name: b"rArr", code: 8658 },
        Ent { name: b"dArr", code: 8659 },
        Ent { name: b"hArr", code: 8660 },
        Ent { name: b"forall", code: 8704 },
        Ent { name: b"part", code: 8706 },
        Ent { name: b"exist", code: 8707 },
        Ent { name: b"empty", code: 8709 },
        Ent { name: b"nabla", code: 8711 },
        Ent { name: b"isin", code: 8712 },
        Ent { name: b"notin", code: 8713 },
        Ent { name: b"ni", code: 8715 },
        Ent { name: b"prod", code: 8719 },
        Ent { name: b"sum", code: 8721 },
        Ent { name: b"minus", code: 8722 },
        Ent { name: b"lowast", code: 8727 },
        Ent { name: b"radic", code: 8730 },
        Ent { name: b"prop", code: 8733 },
        Ent { name: b"infin", code: 8734 },
        Ent { name: b"ang", code: 8736 },
        Ent { name: b"and", code: 8743 },
        Ent { name: b"or", code: 8744 },
        Ent { name: b"cap", code: 8745 },
        Ent { name: b"cup", code: 8746 },
        Ent { name: b"int", code: 8747 },
        Ent { name: b"there4", code: 8756 },
        Ent { name: b"sim", code: 8764 },
        Ent { name: b"cong", code: 8773 },
        Ent { name: b"asymp", code: 8776 },
        Ent { name: b"ne", code: 8800 },
        Ent { name: b"equiv", code: 8801 },
        Ent { name: b"le", code: 8804 },
        Ent { name: b"ge", code: 8805 },
        Ent { name: b"sub", code: 8834 },
        Ent { name: b"sup", code: 8835 },
        Ent { name: b"nsub", code: 8836 },
        Ent { name: b"sube", code: 8838 },
        Ent { name: b"supe", code: 8839 },
        Ent { name: b"oplus", code: 8853 },
        Ent { name: b"otimes", code: 8855 },
        Ent { name: b"perp", code: 8869 },
        Ent { name: b"sdot", code: 8901 },
        Ent { name: b"lceil", code: 8968 },
        Ent { name: b"rceil", code: 8969 },
        Ent { name: b"lfloor", code: 8970 },
        Ent { name: b"rfloor", code: 8971 },
        Ent { name: b"lang", code: 9001 },
        Ent { name: b"rang", code: 9002 },
        Ent { name: b"loz", code: 9674 },
        Ent { name: b"spades", code: 9824 },
        Ent { name: b"clubs", code: 9827 },
        Ent { name: b"hearts", code: 9829 },
        Ent { name: b"diams", code: 9830 },
    ]
}

/// `struct _mbfl_convert_filter` (mbfl_convert.h:40-54). `cache` IS an `i32`.
pub struct Filt {
    pub status: i32,
    pub cache: i32,
}

/// The whole kernel state, as a ghost value. `Ctx::g()` builds it.
pub struct G {
    pub a: Seq<u8>,
    pub bump: Seq<usize>,
    pub blk: Seq<(i32, bool)>,
    pub nblk: usize,
    pub region: usize,
    pub n_alloc: u64,
    pub n_free: u64,
    pub n_dfree: u64,
    pub n_wfree: u64,
    pub bytes: u64,
    pub out: u64,
    pub em: u64,
}

pub open spec fn mix(a: u64, b: u64) -> u64 {
    a.wrapping_mul(31).wrapping_add(b)
}

/// C `char` on x86-64 is SIGNED, and `buffer[pos] - '0'` depends on it.
pub open spec fn sx(b: u8) -> i32 {
    b as i8 as i32
}

/// `strchr(html_entity_chars, c) != NULL` -- mbfilter_htmlent.c:225.
/// ⚠ The `c == 0` arm is `strchr`'s, not an addition; `controls/strchr_equiv.c`.
pub open spec fn s_is_ec(c: i32) -> bool {
    c == 0 || c == 0x23 || (0x30 <= c && c <= 0x39) || (0x61 <= c && c <= 0x7A)
        || (0x41 <= c && c <= 0x5A)
}

pub open spec fn s_emit(g: G, c: i32) -> G {
    G { out: mix(g.out, c as u32 as u64), em: g.em.wrapping_add(1), ..g }
}

/// `ph45_pl_malloc`, post-state. `s_alloc_r` is the value it returns.
pub open spec fn s_alloc_g(g: G, n: usize) -> G {
    let r = g.region as int;
    let g1 = G { n_alloc: g.n_alloc.wrapping_add(1), ..g };
    if n > BLOCK || g1.bump[r] + BLOCK > REGION {
        g1
    } else {
        let idx = g.region * REGION + g1.bump[r];
        let g2 = G {
            bump: g1.bump.update(r, (g1.bump[r] + BLOCK) as usize),
            bytes: g1.bytes.wrapping_add(BLOCK as u64),
            ..g1
        };
        if g2.nblk < NBLK {
            G {
                blk: g2.blk.update(g2.nblk as int, (idx as i32, true)),
                nblk: (g2.nblk + 1) as usize,
                ..g2
            }
        } else {
            g2
        }
    }
}

pub open spec fn s_alloc_r(g: G, n: usize) -> i32 {
    let r = g.region as int;
    if n > BLOCK || g.bump[r] + BLOCK > REGION {
        0
    } else {
        (g.region * REGION + g.bump[r]) as i32
    }
}

pub open spec fn s_free_n(g: G, p: i32, i: int) -> G
    decreases g.nblk - i,
{
    if i < 0 || i >= g.nblk {
        G { n_wfree: g.n_wfree.wrapping_add(1), ..g }
    } else if g.blk[i].0 == p {
        if g.blk[i].1 {
            G { blk: g.blk.update(i, (p, false)), n_free: g.n_free.wrapping_add(1), ..g }
        } else {
            G { n_dfree: g.n_dfree.wrapping_add(1), ..g }
        }
    } else {
        s_free_n(g, p, i + 1)
    }
}

pub open spec fn s_live_n(g: G, i: int, n: u64) -> u64
    decreases g.nblk - i,
{
    if i < 0 || i >= g.nblk {
        n
    } else {
        s_live_n(g, i + 1, if g.blk[i].1 { (n + 1) as u64 } else { n })
    }
}

/// `strcmp(buffer + 1, name) == 0`, with the declared length guard.
pub open spec fn s_name_eq(a: Seq<u8>, buffer: int, name: Seq<u8>) -> bool {
    if name.len() + 2 > REQ {
        false
    } else {
        (forall|k: int| 0 <= k < name.len() ==> a[buffer + 1 + k] == name[k])
            && a[buffer + 1 + name.len()] == 0
    }
}

/// `mbfilter_htmlent.c:200-207`, the linear scan.
pub open spec fn s_lookup(t: Seq<Ent>, a: Seq<u8>, buffer: int, i: int) -> i32
    decreases t.len() - i,
{
    if i < 0 || i >= t.len() {
        0
    } else if s_name_eq(a, buffer, t[i].name@) {
        t[i].code
    } else {
        s_lookup(t, a, buffer, i + 1)
    }
}

/// `mbfilter_htmlent.c:192-194`, the numeric accumulate.
pub open spec fn s_num(a: Seq<u8>, buffer: int, status: int, pos: int, ent: i32) -> i32
    decreases status - pos,
{
    if pos >= status {
        ent
    } else {
        s_num(
            a,
            buffer,
            status,
            pos + 1,
            (ent as u32).wrapping_mul(10).wrapping_add((sx(a[buffer + pos]) - 0x30) as u32) as i32,
        )
    }
}

/// `mbfilter_htmlent.c:252-254`, the flush loop.
pub open spec fn s_flush_n(g: G, buffer: int, status: int, pos: int) -> G
    decreases status,
{
    if status <= 0 {
        g
    } else {
        s_flush_n(s_emit(g, sx(g.a[buffer + pos])), buffer, status - 1, pos + 1)
    }
}

pub open spec fn s_flush(g: G, f: Filt) -> (G, Filt) {
    (s_flush_n(g, f.cache as int, f.status as int, 0), Filt { status: 0, cache: f.cache })
}

/// `mbfilter_htmlent.c:174-242`. The mirror is branch for branch.
pub open spec fn s_dec(g: G, f: Filt, c: i32) -> (G, Filt) {
    let buffer = f.cache as int;
    if f.status == 0 {
        if c == 0x26 {
            (G { a: g.a.update(buffer, 0x26), ..g }, Filt { status: 1, cache: f.cache })
        } else {
            (s_emit(g, c), f)
        }
    } else if c == 0x3B {
        let g0 = G { a: g.a.update(buffer + f.status as int, 0), ..g };
        if g0.a[buffer + 1] == 0x23 {
            let ent = s_num(g0.a, buffer, f.status as int, 2, 0);
            (s_emit(g0, ent), Filt { status: 0, cache: f.cache })
        } else {
            let ent = s_lookup(tbl(), g0.a, buffer, 0);
            if ent != 0 {
                (s_emit(g0, ent), Filt { status: 0, cache: f.cache })
            } else {
                let g1 = G { a: g0.a.update(buffer + f.status as int, 0x3B), ..g0 };
                let st1 = (f.status + 1) as i32;
                let g2 = G { a: g1.a.update(buffer + st1 as int, 0), ..g1 };
                s_flush(g2, Filt { status: st1, cache: f.cache })
            }
        }
    } else {
        let g0 = G { a: g.a.update(buffer + f.status as int, c as u8), ..g };
        let st1 = (f.status + 1) as i32;
        if !s_is_ec(c) || st1 + 1 == HTML_ENC_BUFFER_SIZE || (c == 0x23 && st1 > 2) {
            let st2 = if c == 0x26 { (st1 - 1) as i32 } else { st1 };
            let g1 = G { a: g0.a.update(buffer + st2 as int, 0), ..g0 };
            let r = s_flush(g1, Filt { status: st2, cache: f.cache });
            if c == 0x26 {
                (G { a: r.0.a.update(buffer, 0x26), ..r.0 }, Filt { status: 1, cache: f.cache })
            } else {
                r
            }
        } else {
            (g0, Filt { status: st1, cache: f.cache })
        }
    }
}

/// `mbfl_buffer_converter_feed`, mbfilter.c:262-267, over two converters.
pub open spec fn s_feed(g: G, fa: Filt, fb: Filt, win: Seq<u8>, i: int, len: int) -> (G, Filt, Filt)
    decreases len - i,
{
    if i < HEAD || i >= len {
        (g, fa, fb)
    } else {
        let c = win[i] as i32;
        if (i - HEAD) % 2 == 1 {
            let r = s_dec(g, fb, c);
            s_feed(r.0, fa, r.1, win, i + 1, len)
        } else {
            let r = s_dec(g, fa, c);
            s_feed(r.0, r.1, fb, win, i + 1, len)
        }
    }
}

pub open spec fn s_dtor(g: G, f: Filt) -> G {
    if f.cache != 0 {
        s_free_n(g, f.cache, 0)
    } else {
        g
    }
}

pub open spec fn s_init() -> G {
    G {
        a: Seq::new(ASZ as nat, |i: int| 0u8),
        bump: Seq::new(2nat, |i: int| BLOCK),
        blk: Seq::new(NBLK as nat, |i: int| (0i32, false)),
        nblk: 0,
        region: 0,
        n_alloc: 0,
        n_free: 0,
        n_dfree: 0,
        n_wfree: 0,
        bytes: 0,
        out: 0,
        em: 0,
    }
}

pub open spec fn s_rd32(w: Seq<u8>, i: int) -> u32 {
    (w[i] as u32) | ((w[i + 1] as u32) << 8u32) | ((w[i + 2] as u32) << 16u32)
        | ((w[i + 3] as u32) << 24u32)
}

/// ⚠ OPAQUE. Without this, Z3 unfolds the whole composition into `kernel`'s
/// one-line postcondition and then matches that term tree against the same tree
/// with differently-spelled arguments -- which is `ph64`'s lesson (its
/// `twin_obligations_note`) and it blows any budget.
#[verifier::opaque]
pub open spec fn run_spec(win: Seq<u8>, len: int) -> u64 {
    let place = s_rd32(win, 0) & 3;
    let order = s_rd32(win, 4) & 1;
    let g0 = G { region: (place & 1) as usize, ..s_init() };
    let ca = s_alloc_r(g0, REQ);
    let g1 = G { region: ((place >> 1u32) & 1) as usize, ..s_alloc_g(g0, REQ) };
    let cb = s_alloc_r(g1, REQ);
    let g2 = s_alloc_g(g1, REQ);
    let fa0 = Filt { status: 0, cache: ca };
    let fb0 = Filt { status: 0, cache: cb };
    let r = s_feed(g2, fa0, fb0, win, HEAD as int, len);
    let ra = s_flush(r.0, r.1);
    let rb = s_flush(ra.0, r.2);
    let acc0 = mix(rb.0.out, rb.0.em);
    let gd = if order == 1 {
        s_dtor(s_dtor(rb.0, r.2), r.1)
    } else {
        s_dtor(s_dtor(rb.0, r.1), r.2)
    };
    let live = s_live_n(gd, 0, 0);
    let a1 = mix(acc0, gd.n_alloc);
    let a2 = mix(a1, gd.n_free);
    let a3 = mix(a2, gd.n_dfree);
    let a4 = mix(a3, gd.n_wfree);
    let a5 = mix(a4, live);
    let a6 = mix(a5, gd.bytes);
    mix(mix(mix(a6, 2), 2), 0)
}

pub open spec fn html_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    run_spec(buf.subrange(off, off + len), len)
}

// =========================================================================
// exec
// =========================================================================

pub struct Ctx {
    pub arena: [u8; ASZ],
    pub bump: [usize; 2],
    pub blk: [(i32, bool); NBLK],
    pub nblk: usize,
    pub region: usize,
    pub n_alloc: u64,
    pub n_free: u64,
    pub n_dfree: u64,
    pub n_wfree: u64,
    pub bytes: u64,
    pub out: u64,
    pub emitted: u64,
}

impl Ctx {
    pub open spec fn g(&self) -> G {
        G {
            a: self.arena@,
            bump: self.bump@,
            blk: self.blk@,
            nblk: self.nblk,
            region: self.region,
            n_alloc: self.n_alloc,
            n_free: self.n_free,
            n_dfree: self.n_dfree,
            n_wfree: self.n_wfree,
            bytes: self.bytes,
            out: self.out,
            em: self.emitted,
        }
    }
}

/// The structural invariant. ⭐ `wf_f` IS obligation O2: *"the value read back
/// out of the narrow field designates the block the allocator returned"*.
pub open spec fn wf_c(c: Ctx) -> bool {
    &&& c.arena@.len() == ASZ
    &&& c.bump@.len() == 2
    &&& c.bump@[0] <= REGION
    &&& c.bump@[1] <= REGION
    &&& c.blk@.len() == NBLK
    &&& c.nblk <= NBLK
    &&& c.region < 2
}

/// ⭐ `wf_ptr` IS OBLIGATION O2, and it is the whole of what the C assumes and
/// never establishes: the value read back out of the narrow field still
/// designates the 32-byte block the allocator returned.
pub open spec fn wf_ptr(f: Filt) -> bool {
    &&& 0 < f.cache
    &&& f.cache + BLOCK <= ASZ
}

/// ⚠ THE STATUS BOUND IS 14 AND NOT 16, AND THE TWO IT LEAVES ARE THE ROW'S
/// TIGHTEST PIECE OF REASONING. `mbfilter_htmlent.c:223` writes `buffer[status]`
/// and increments, and `:225` resets to 0 the moment `status + 1 == 16` -- so a
/// filter that is BETWEEN characters carries `status <= 14`. Inside `:213-218`
/// it reaches 15 for two statements (`buffer[status++] = ';'` then
/// `buffer[status] = 0`), which is why `dec_flush` accepts 15 and `wf_f` does
/// not. 15 is also the largest index this kernel ever writes, and the block is
/// 32 bytes: the C's `html_enc_buffer_size + 1` request has one byte of slack
/// and `mbfl_malloc` has fifteen.
pub open spec fn wf_f(f: Filt) -> bool {
    &&& wf_ptr(f)
    &&& 0 <= f.status <= HTML_ENC_BUFFER_SIZE - 2
}

/// ⚠ TRUSTED #1. `get_unchecked` is defined only while `i < ASZ`; vstd ships no
/// spec for it. The twin below is the safe body with the same contract.
#[verifier::external_body]
fn bget(v: &[u8; ASZ], i: usize) -> (r: u8)
    requires
        i < ASZ,
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_bget(v: &[u8; ASZ], i: usize) -> (r: u8)
    requires
        i < ASZ,
    ensures
        r == v@[i as int],
{
    v[i]
}

/// ⚠ TRUSTED #2. `x: u8` is a PURE VALUE -- all 256 inhabitants are a legal
/// store into a byte `[0u8; ASZ]` already initialised -- so the precondition is
/// about `i` alone. ⚠⚠ THE `ensures` NAMES THE WHOLE POST-STATE, not just
/// `v@[i]`: an `ensures` that named only the written slot would license a body
/// that also moved a neighbour, and on this row the neighbour is the OTHER
/// filter's work buffer.
#[verifier::external_body]
fn bset(v: &mut [u8; ASZ], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
fn slb_twin_bset(v: &mut [u8; ASZ], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
    assert(final(v)@ =~= old(v)@.update(i as int, x));
}

fn rd32(w: &[u8], i: usize) -> (r: u32)
    requires
        i + 4 <= w@.len(),
    ensures
        r == s_rd32(w@, i as int),
{
    (w[i] as u32) | ((w[i + 1] as u32) << 8u32) | ((w[i + 2] as u32) << 16u32)
        | ((w[i + 3] as u32) << 24u32)
}

fn is_entity_char(c: i32) -> (r: bool)
    ensures
        r == s_is_ec(c),
{
    c == 0 || c == 0x23 || (0x30 <= c && c <= 0x39) || (0x61 <= c && c <= 0x7A)
        || (0x41 <= c && c <= 0x5A)
}

impl Ctx {
    fn new() -> (r: Ctx)
        ensures
            r.g() == s_init(),
            wf_c(r),
    {
        let ctx = Ctx {
            arena: [0u8; ASZ],
            bump: [BLOCK, BLOCK],
            blk: [(0i32, false); NBLK],
            nblk: 0,
            region: 0,
            n_alloc: 0,
            n_free: 0,
            n_dfree: 0,
            n_wfree: 0,
            bytes: 0,
            out: 0,
            emitted: 0,
        };
        assert(ctx.arena@ =~= Seq::new(ASZ as nat, |i: int| 0u8));
        assert(ctx.bump@ =~= Seq::new(2nat, |i: int| BLOCK));
        assert(ctx.blk@ =~= Seq::new(NBLK as nat, |i: int| (0i32, false)));
        assert(ctx.g() =~= s_init());
        ctx
    }

    /// `ph45_pl_malloc`. The third `ensures` is OBLIGATION O1 written out: the
    /// index it returns is 0 or lies in `[BLOCK, ASZ - BLOCK]`, so storing it in
    /// an `i32` and reading it back is the IDENTITY.
    ///
    /// ⚠⚠ AND IT IS REDUNDANT, MEASURED RATHER THAN ASSUMED. Deleting that line
    /// still verifies **41 / 0** (`.temp/php36/logs-04-vacuity.log`, mutant V2),
    /// because `r == s_alloc_r(old(self).g(), n)` plus `wf_c`'s
    /// `bump[r] <= REGION` already pin the range. It is KEPT because it is the
    /// only place in the file where O1 is legible as O1, and what actually
    /// carries it is `wf_c`'s bump bound -- mutant V4 deletes THAT and the proof
    /// fails with `possible arithmetic underflow/overflow` (40 / 1).
    /// ⭐ A declaration that cannot fail is worth writing only if you have
    /// measured that it cannot; this one has.
    fn alloc(&mut self, n: usize) -> (r: i32)
        requires
            wf_c(*old(self)),
        ensures
            final(self).g() == s_alloc_g(old(self).g(), n),
            r == s_alloc_r(old(self).g(), n),
            r == 0 || (0 < r && r + BLOCK <= ASZ),
            wf_c(*final(self)),
    {
        let r: usize = self.region;
        self.n_alloc = self.n_alloc.wrapping_add(1);
        if n > BLOCK || self.bump[r] + BLOCK > REGION {
            return 0;
        }
        let idx: usize = r * REGION + self.bump[r];
        self.bump[r] = self.bump[r] + BLOCK;
        self.bytes = self.bytes.wrapping_add(BLOCK as u64);
        if self.nblk < NBLK {
            self.blk[self.nblk] = (idx as i32, true);
            self.nblk = self.nblk + 1;
        }
        idx as i32
    }

    /// `ph45_pl_free`. ⭐ OBLIGATION O3 lives here and it is a VALUE fact, not a
    /// memory-safety one: handing this the wrong index is a wrong answer, not a
    /// wrong access.
    fn free(&mut self, p: i32)
        requires
            wf_c(*old(self)),
        ensures
            final(self).g() == s_free_n(old(self).g(), p, 0),
            wf_c(*final(self)),
    {
        let mut i: usize = 0;
        while i < self.nblk
            invariant
                i <= self.nblk,
                self.nblk <= NBLK,
                wf_c(*self),
                self.g() == old(self).g(),
                s_free_n(old(self).g(), p, 0) == s_free_n(self.g(), p, i as int),
            decreases self.nblk - i,
        {
            if self.blk[i].0 == p {
                if self.blk[i].1 {
                    proof {
                        reveal(s_free_n);
                    }
                    self.blk[i] = (p, false);
                    self.n_free = self.n_free.wrapping_add(1);
                } else {
                    self.n_dfree = self.n_dfree.wrapping_add(1);
                }
                return;
            }
            i = i + 1;
        }
        self.n_wfree = self.n_wfree.wrapping_add(1);
    }

    fn live(&self) -> (r: u64)
        requires
            wf_c(*self),
        ensures
            r == s_live_n(self.g(), 0, 0),
    {
        let mut n: u64 = 0;
        let mut i: usize = 0;
        while i < self.nblk
            invariant
                i <= self.nblk,
                self.nblk <= NBLK,
                n <= i,
                s_live_n(self.g(), 0, 0) == s_live_n(self.g(), i as int, n),
            decreases self.nblk - i,
        {
            if self.blk[i].1 {
                n = n + 1;
            }
            i = i + 1;
        }
        n
    }

    fn emit(&mut self, c: i32)
        ensures
            final(self).g() == s_emit(old(self).g(), c),
    {
        self.out = self.out.wrapping_mul(31).wrapping_add(c as u32 as u64);
        self.emitted = self.emitted.wrapping_add(1);
    }
}

/// `mbfilter_htmlent.c:158-162`. ⚠⚠ `:161`'s NARROWING STORE.
fn dec_ctor(ctx: &mut Ctx, f: &mut Filt, region: usize)
    requires
        wf_c(*old(ctx)),
        region < 2,
    ensures
        final(ctx).g() == s_alloc_g((G { region, ..old(ctx).g() }), REQ),
        final(f).cache == s_alloc_r((G { region, ..old(ctx).g() }), REQ),
        final(f).status == 0,
        final(f).cache == 0 || (0 < final(f).cache && final(f).cache + BLOCK <= ASZ),
        wf_c(*final(ctx)),
{
    f.status = 0;
    ctx.region = region;
    let p: i32 = ctx.alloc(REQ);
    f.cache = p;
}

/// `mbfilter_htmlent.c:164-172`.
fn dec_dtor(ctx: &mut Ctx, f: &mut Filt)
    requires
        wf_c(*old(ctx)),
    ensures
        final(ctx).g() == s_dtor(old(ctx).g(), *old(f)),
        wf_c(*final(ctx)),
{
    f.status = 0;
    if f.cache != 0 {
        ctx.free(f.cache);
    }
    f.cache = 0;
}

/// `strcmp(buffer + 1, name) == 0`. The length guard is declared in
/// `unsafe.rs`'s header and is never taken.
fn name_eq(ctx: &Ctx, buffer: usize, name: &[u8]) -> (r: bool)
    requires
        wf_c(*ctx),
        buffer + BLOCK <= ASZ,
    ensures
        r == s_name_eq(ctx.arena@, buffer as int, name@),
{
    let n: usize = name.len();
    if n > REQ - 2 {
        return false;
    }
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n + 2 <= REQ,
            buffer + BLOCK <= ASZ,
            ctx.arena@.len() == ASZ,
            n == name@.len(),
            forall|k: int| 0 <= k < i ==> ctx.arena@[buffer + 1 + k] == name@[k],
        decreases n - i,
    {
        if bget(&ctx.arena, buffer + 1 + i) != name[i] {
            return false;
        }
        i = i + 1;
    }
    bget(&ctx.arena, buffer + 1 + n) == 0
}

/// `mbfilter_htmlent.c:244-257`. ⚠ `:249` is the SECOND read-back.
fn dec_flush(ctx: &mut Ctx, f: &mut Filt)
    requires
        wf_c(*old(ctx)),
        wf_ptr(*old(f)),
        0 <= old(f).status <= HTML_ENC_BUFFER_SIZE - 1,
    ensures
        (final(ctx).g(), *final(f)) == s_flush(old(ctx).g(), *old(f)),
        wf_c(*final(ctx)),
        final(f).cache == old(f).cache,
        final(f).status == 0,
{
    let buffer: usize = f.cache as usize;
    let mut status: i32 = f.status;
    let mut pos: usize = 0;
    while status != 0
        invariant
            0 <= status <= HTML_ENC_BUFFER_SIZE - 1,
            pos == f.status - status,
            0 <= pos,
            buffer == f.cache as usize,
            wf_ptr(*f),
            0 <= f.status <= HTML_ENC_BUFFER_SIZE - 1,
            wf_c(*ctx),
            buffer + BLOCK <= ASZ,
            s_flush_n(old(ctx).g(), buffer as int, f.status as int, 0)
                == s_flush_n(ctx.g(), buffer as int, status as int, pos as int),
        decreases status,
    {
        status = status - 1;
        let v: i32 = bget(&ctx.arena, buffer + pos) as i8 as i32;
        ctx.emit(v);
        pos = pos + 1;
    }
    f.status = 0;
    proof {
        assert((ctx.g(), *f) =~= s_flush(old(ctx).g(), *old(f)));
    }
}

/// `mbfilter_htmlent.c:174-242`. ⚠⚠ `:178` is the FIRST read-back, it SIGN
/// EXTENDS, and every access below is unchecked. What discharges each one is
/// `wf_f` -- obligation O2.
/// ⚠⚠ `#[cfg_attr(slb_isolated, inline(never))]` ON `dec` IS A MEASUREMENT
/// DECISION AND IT IS DECLARED HERE. `measure.py`'s `kernel_exclusive_ir` sums
/// only symbols matching `(^|::)kernel($|[^A-Za-z0-9_])`, so whether `dec` is
/// inlined decides whether 90 % of the row's work is inside that number or
/// outside it. In C `dec` is `mbfl_filt_conv_html_dec` reached through
/// `filter->filter_function` -- a call through a POINTER, which gcc and clang
/// both leave out of line -- so the C's `kernel_exclusive_ir` EXCLUDES the
/// filter body. Left to LLVM the four Rust rungs did not agree with each other:
/// R2/R3/R4 kept `dec` out of line and R5 inlined it, which made R5's
/// `kernel_exclusive_ir` 76.2 M against R4's 7.8 M -- a 10x number that is not
/// a cost at all, only a different denominator. Pinning it here makes all six
/// rungs attribute the same way. `../NOTES.md` section 8.
#[cfg_attr(slb_isolated, inline(never))]
fn dec(ctx: &mut Ctx, f: &mut Filt, c: i32)
    requires
        wf_c(*old(ctx)),
        wf_f(*old(f)),
        0 <= c < 256,
    ensures
        (final(ctx).g(), *final(f)) == s_dec(old(ctx).g(), *old(f), c),
        wf_c(*final(ctx)),
        wf_f(*final(f)),
{
    let ghost g0 = ctx.g();
    let ghost f0 = *f;
    let mut ent: i32 = 0;
    let buffer: usize = f.cache as usize;

    if f.status == 0 {
        if c == 0x26 {
            f.status = 1;
            bset(&mut ctx.arena, buffer, 0x26);
        } else {
            ctx.emit(c);
        }
    } else if c == 0x3B {
        bset(&mut ctx.arena, buffer + f.status as usize, 0);
        if bget(&ctx.arena, buffer + 1) == 0x23 {
            let mut pos: i32 = 2;
            while pos < f.status
                invariant
                    2 <= pos <= f.status,
                    f.status <= HTML_ENC_BUFFER_SIZE - 2,
                    buffer == f.cache as usize,
                    buffer + BLOCK <= ASZ,
                    wf_c(*ctx),
                    ctx.g() == (G { a: g0.a.update(buffer + f0.status as int, 0), ..g0 }),
                    s_num(ctx.arena@, buffer as int, f.status as int, 2, 0)
                        == s_num(ctx.arena@, buffer as int, f.status as int, pos as int, ent),
                decreases f.status - pos,
            {
                let d: i32 = bget(&ctx.arena, buffer + pos as usize) as i8 as i32;
                ent = (ent as u32).wrapping_mul(10).wrapping_add((d - 0x30) as u32) as i32;
                pos = pos + 1;
            }
            ctx.emit(ent);
            f.status = 0;
        } else {
            let t: &[Ent] = ent_table();
            let mut i: usize = 0;
            let mut found: bool = false;
            while i < t.len() && !found
                invariant
                    i <= t.len(),
                    t@ == tbl(),
                    buffer == f.cache as usize,
                    buffer + BLOCK <= ASZ,
                    wf_c(*ctx),
                    ctx.g() == (G { a: g0.a.update(buffer + f0.status as int, 0), ..g0 }),
                    !found ==> ent == 0,
                    !found ==> s_lookup(tbl(), ctx.arena@, buffer as int, 0)
                        == s_lookup(tbl(), ctx.arena@, buffer as int, i as int),
                    found ==> ent == s_lookup(tbl(), ctx.arena@, buffer as int, 0),
                decreases t.len() - i, if found { 0int } else { 1int },
            {
                if name_eq(ctx, buffer, t[i].name) {
                    ent = t[i].code;
                    found = true;
                }
                i = i + 1;
            }
            if ent != 0 {
                ctx.emit(ent);
                f.status = 0;
            } else {
                bset(&mut ctx.arena, buffer + f.status as usize, 0x3B);
                f.status = f.status + 1;
                bset(&mut ctx.arena, buffer + f.status as usize, 0);
                dec_flush(ctx, f);
            }
        }
    } else {
        bset(&mut ctx.arena, buffer + f.status as usize, c as u8);
        f.status = f.status + 1;
        if !is_entity_char(c) || f.status + 1 == HTML_ENC_BUFFER_SIZE || (c == 0x23 && f.status
            > 2) {
            if c == 0x26 {
                f.status = f.status - 1;
            }
            bset(&mut ctx.arena, buffer + f.status as usize, 0);
            dec_flush(ctx, f);
            if c == 0x26 {
                f.status = 1;
                bset(&mut ctx.arena, buffer, 0x26);
            }
        }
    }
}

/// ⚠ SPLIT FROM `run` DELIBERATELY, AND THE ORDER IS THE POINT. `ph64`'s
/// `twin_obligations_note` records the same thing: with the whole composition
/// inline, Z3 unfolds `run_spec` into `kernel`'s one-line postcondition, unfolds
/// four recursive spec functions inside it once each by default fuel, and then
/// matches that term tree against the same tree with differently-spelled
/// arguments. Opaque and split, the match is two arguments.
/// ⚠ `#[cfg_attr(slb_isolated, inline(never))]` IS NOT COSMETIC: without it
/// LLVM inlines `kernel` into the driver loop and `measure.py` reports
/// `kernel_exclusive_ir = None` for every Rust cell, so the row has no A1
/// statistic at all. The C side gets the same thing from `SLB_NOINLINE`.
#[cfg_attr(slb_isolated, inline(never))]
fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        16 <= len,
        len <= 268435456,
    ensures
        r == html_fold(buf@, off as int, len as int),
{
    proof {
        // `axiom_spec_len` (broadcast above) gives `spec_slice_len(buf) ==
        // buf@.len()`, and `spec_slice_len` is a `usize` -- which is the only
        // route to `off + len` not overflowing.
        assert(vstd::slice::spec_slice_len(buf) == buf@.len());
    }
    let win: &[u8] = slice_subrange(buf, off, off + len);
    run(win, len)
}

#[verifier::rlimit(60)]
fn run(win: &[u8], len: usize) -> (r: u64)
    requires
        win@.len() == len,
        16 <= len,
        len <= 268435456,
    ensures
        r == run_spec(win@, len as int),
{
    proof {
        reveal(run_spec);
    }
    let place: u32 = rd32(win, 0) & 3;
    let order: u32 = rd32(win, 4) & 1;

    let mut ctx: Ctx = Ctx::new();
    let mut fa: Filt = Filt { status: 0, cache: 0 };
    let mut fb: Filt = Filt { status: 0, cache: 0 };
    assert((place & 1) < 2) by (bit_vector);
    assert(((place >> 1u32) & 1) < 2) by (bit_vector);
    dec_ctor(&mut ctx, &mut fa, (place & 1) as usize);
    dec_ctor(&mut ctx, &mut fb, ((place >> 1u32) & 1) as usize);

    let ghost ge = ctx.g();
    let ghost fae = fa;
    let ghost fbe = fb;
    let mut i: usize = HEAD;
    // ⚠ THE REMAINING-COMPUTATION INVARIANT, not a prefix one. `s_feed` recurses
    // FORWARD from `i` to `len`, so what stays constant is the whole rest of the
    // fold seen from the current state -- which is `ph64`'s lockstep-ghost-mirror
    // shape and the only one that closes at `i == len` without a separate
    // append lemma.
    while i < len
        invariant
            HEAD <= i <= len,
            win@.len() == len,
            wf_c(ctx),
            wf_f(fa),
            wf_f(fb),
            s_feed(ge, fae, fbe, win@, HEAD as int, len as int) == s_feed(
                ctx.g(),
                fa,
                fb,
                win@,
                i as int,
                len as int,
            ),
        decreases len - i,
    {
        let c: i32 = win[i] as i32;
        if (i - HEAD) % 2 == 1 {
            dec(&mut ctx, &mut fb, c);
        } else {
            dec(&mut ctx, &mut fa, c);
        }
        i = i + 1;
    }
    dec_flush(&mut ctx, &mut fa);
    dec_flush(&mut ctx, &mut fb);

    let mut acc: u64 = ctx.out;
    acc = acc.wrapping_mul(31).wrapping_add(ctx.emitted);

    if order == 1 {
        dec_dtor(&mut ctx, &mut fb);
        dec_dtor(&mut ctx, &mut fa);
    } else {
        dec_dtor(&mut ctx, &mut fa);
        dec_dtor(&mut ctx, &mut fb);
    }

    let live: u64 = ctx.live();
    acc = acc.wrapping_mul(31).wrapping_add(ctx.n_alloc);
    acc = acc.wrapping_mul(31).wrapping_add(ctx.n_free);
    acc = acc.wrapping_mul(31).wrapping_add(ctx.n_dfree);
    acc = acc.wrapping_mul(31).wrapping_add(ctx.n_wfree);
    acc = acc.wrapping_mul(31).wrapping_add(live);
    acc = acc.wrapping_mul(31).wrapping_add(ctx.bytes);
    acc = acc.wrapping_mul(31).wrapping_add(2);
    acc = acc.wrapping_mul(31).wrapping_add(2);
    acc = acc.wrapping_mul(31).wrapping_add(0);
    acc
}

#[verifier::external_body]
fn load_input() -> (r: (u64, Vec<u8>, u64)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (stride_w, bytes, inp.n_iters)
}

/// ⚠ NAMED `emit_result` AND NOT `emit`: `Ctx::emit` already exists, and
/// `vparse.unique_names` RAISES on two items sharing a name that no scope
/// distinguishes -- which took out five gate stages at once on this row's first
/// run (`proof-rule2`, `clause-mut`, `req-mut`, `twin`, `contract-source`).
#[verifier::external_body]
fn emit_result(acc: u64) {
    driver::emit(acc);
}

fn main() {
    let (stride_w, bytes, n_iters) = load_input();

    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                16 <= stride <= n_blob,
                stride <= 268435456,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            proof {
                let pr: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pr < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pr == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_blob as int,
                    stride as int,
                );
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            assert(r == html_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit_result(acc);
}

} // verus!
