//! ph45 rung R4 -- unsafe Rust. The same function as `safe_tuned.rs` with the
//! bounds checks removed: every one of `mbfl_filt_conv_html_dec`'s eleven
//! dereferences goes through `bget` / `bset`, which are `get_unchecked` /
//! `get_unchecked_mut` on the arena.
//!
//! ============================================================================
//! ⚠⚠⚠ R4 IS NOT A PORT OF R1, AND ON THIS ROW THAT NEEDS SAYING TWICE
//! ============================================================================
//! `.memory-php/02-ladder.md`: *"the hardened C rung carries the historical fix,
//! the Rust rungs carry whatever is actually memory-safe."*
//!
//! ⭐ AND HERE THE MEMORY-SAFE SPELLING IS **R1's OWN IDIOM**. `cache` is an
//! `i32` exactly as at `mbfl_convert.h:49`; the store is `idx as i32` exactly as
//! at `mbfilter_htmlent.c:161`; the read-back is `cache as usize` exactly as at
//! `:178` and `:249`, sign extension included. Nothing is widened and `void
//! *opaque` appears nowhere. What makes the C unsafe is not the shape of the
//! code -- it is that the value stored is an ADDRESS, and addresses on this
//! platform need 47 bits. The value stored here is an INDEX into an arena the
//! kernel owns, and 512 needs nine.
//!
//! ⚠⚠ SO THE ROW'S OBLIGATION IS NOT DISCHARGED BY RUST, IT IS RELOCATED.
//! `bget(v, i)` is sound only while `i < ASZ`, and `i` is `cache as usize + k`.
//! In C nothing establishes that. In R4 it is an `unsafe` block with a comment.
//! In `verus.rs` it is a `requires` that must be DISCHARGED, and what discharges
//! it is `0 < cache <= ASZ - BLOCK` -- i.e. *"the value read back out of the
//! narrow field still designates the block the allocator returned"*, which is
//! the corpus invariant `pointer-value-integrity`'s obligations O1 and O2, word
//! for word. `../NOTES.md` §11.
//!
//! ⚠ AND RUSTC SAYS NOTHING WHERE GCC SAYS FOUR THINGS. Measured
//! (`../NOTES.md` §10): `c/kernel.c` at `-Wall -Wextra` emits
//! `-Wpointer-to-int-cast` once and `-Wint-to-pointer-cast` three times -- the
//! four sites `e8901dc17087` rewrites, i.e. bug #30573 itself. The equivalent
//! Rust, `(&x[0] as *const u8) as i32` followed by `t as usize as *const u8`
//! and a dereference, compiles with **zero diagnostics even under
//! `-D warnings`** and SIGSEGVs when run. The usual story about these two
//! languages runs the other way.

#[path = "../../common/driver.rs"]
mod driver;

const HEAD: usize = 8;
const BLOCK: usize = 32;
const SLOTS: usize = 8;
const REGION: usize = BLOCK * SLOTS;
/// The whole arena: two regions. ⚠ THE C's ARE 2^32 BYTES APART.
const ASZ: usize = 2 * REGION;
const HTML_ENC_BUFFER_SIZE: i32 = 16;
const REQ: usize = 17;

pub struct Ent {
    pub name: &'static [u8],
    pub code: i32,
}

/// `html_entities.c:37-290`, GENERATED -- `controls/entity_table.py`.
/// A function rather than a `static` so that `verus.rs` can carry the same
/// spelling; the two rungs must be byte-comparable.
fn ent_table() -> &'static [Ent] {
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

/// `c/arena.h` plus the projected output device. Index 0 is reserved and never
/// issued, so `cache != 0` is the same guard `mbfilter_htmlent.c:167` writes.
pub struct Ctx {
    pub arena: [u8; ASZ],
    pub bump: [usize; 2],
    pub blk: [(i32, bool); 2 * SLOTS],
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

/// ⚠ TRUSTED #1. `v.get_unchecked(i)` is defined only while `i < ASZ`.
fn bget(v: &[u8; ASZ], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// ⚠ TRUSTED #2. `v.get_unchecked_mut(i)` is defined only while `i < ASZ`.
/// `x: u8` is a pure value: every one of its 256 inhabitants is a legal store
/// into a byte that `[0u8; ASZ]` already initialised.
fn bset(v: &mut [u8; ASZ], i: usize, x: u8) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

fn rd32(w: &[u8], i: usize) -> u32 {
    (w[i] as u32) | ((w[i + 1] as u32) << 8) | ((w[i + 2] as u32) << 16)
        | ((w[i + 3] as u32) << 24)
}

/// `strchr(html_entity_chars, c) != NULL` -- `mbfilter_htmlent.c:225`.
///
/// ⚠⚠ THE `c == 0` ARM IS NOT AN ADDITION, IT IS `strchr`. `strchr(s, 0)`
/// returns a pointer to the TERMINATOR, which is non-NULL, so PHP treats a NUL
/// byte inside an entity body as a legal entity character. Every Rust rung
/// spells the predicate as a range test rather than as a scan over the 63-byte
/// constant, because a proof cannot read a `&'static [u8]` constant's contents;
/// `controls/strchr_equiv.c` drives all 256 byte values against the real
/// `strchr` and carries a MUST-FIRE negative for the predicate that omits this
/// arm (it disagrees exactly once, at `c == 0`).
fn is_entity_char(c: i32) -> bool {
    c == 0 || c == 0x23 || (0x30 <= c && c <= 0x39) || (0x61 <= c && c <= 0x7A)
        || (0x41 <= c && c <= 0x5A)
}

impl Ctx {
    fn new() -> Ctx {
        Ctx { arena: [0u8; ASZ], bump: [BLOCK, BLOCK],
              blk: [(0i32, false); 2 * SLOTS], nblk: 0, region: 0,
              n_alloc: 0, n_free: 0, n_dfree: 0, n_wfree: 0, bytes: 0,
              out: 0, emitted: 0 }
    }

    /// `ph45_pl_malloc`. Returns an INDEX; 0 means NULL.
    fn alloc(&mut self, n: usize) -> i32 {
        let r: usize = self.region;
        self.n_alloc = self.n_alloc.wrapping_add(1);
        if n > BLOCK || self.bump[r] + BLOCK > REGION {
            return 0;
        }
        let idx: usize = r * REGION + self.bump[r];
        self.bump[r] = self.bump[r] + BLOCK;
        self.bytes = self.bytes.wrapping_add(BLOCK as u64);
        if self.nblk < 2 * SLOTS {
            self.blk[self.nblk] = (idx as i32, true);
            self.nblk = self.nblk + 1;
        }
        idx as i32
    }

    /// `ph45_pl_free`. The `n_dfree` / `n_wfree` arms are the ones R1 takes at
    /// a non-zero placement and no Rust rung can.
    fn free(&mut self, p: i32) {
        let mut i: usize = 0;
        while i < self.nblk {
            if self.blk[i].0 == p {
                if self.blk[i].1 {
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

    fn live(&self) -> u64 {
        let mut n: u64 = 0;
        let mut i: usize = 0;
        while i < self.nblk {
            if self.blk[i].1 {
                n = n + 1;
            }
            i = i + 1;
        }
        n
    }

    fn emit(&mut self, c: i32) {
        self.out = self.out.wrapping_mul(31).wrapping_add(c as u32 as u64);
        self.emitted = self.emitted.wrapping_add(1);
    }
}

/// `mbfilter_htmlent.c:158-162`. ⚠⚠ `:161`'s NARROWING STORE.
fn dec_ctor(ctx: &mut Ctx, f: &mut Filt, region: usize) {
    f.status = 0;
    ctx.region = region;
    let p: i32 = ctx.alloc(REQ);
    f.cache = p;
}

/// `mbfilter_htmlent.c:164-172`.
fn dec_dtor(ctx: &mut Ctx, f: &mut Filt) {
    f.status = 0;
    if f.cache != 0 {
        ctx.free(f.cache);
    }
    f.cache = 0;
}

/// `strcmp(buffer + 1, name) == 0`, byte for byte with `strcmp`'s early exit.
///
/// ⚠ THE LENGTH GUARD IS A DIVERGENCE AND IT IS DECLARED. `strcmp` gets its
/// bound from the two NUL terminators; a proof cannot use a bound an argument
/// merely happens to have, so the Rust rungs state it. It is never taken: the
/// longest entity name in `html_entities.c:37-290` is EIGHT characters
/// (measured -- `controls/entity_table.py` prints it) and `REQ` is 17.
fn name_eq(ctx: &Ctx, buffer: usize, name: &[u8]) -> bool {
    let n: usize = name.len();
    if n + 2 > REQ {
        return false;
    }
    let mut i: usize = 0;
    while i < n {
        if bget(&ctx.arena, buffer + 1 + i) != name[i] {
            return false;
        }
        i = i + 1;
    }
    bget(&ctx.arena, buffer + 1 + n) == 0
}

/// `mbfilter_htmlent.c:244-257`. ⚠ `:249` is the SECOND read-back.
fn dec_flush(ctx: &mut Ctx, f: &mut Filt) {
    let buffer: usize = f.cache as usize;
    let mut status: i32 = f.status;
    let mut pos: usize = 0;
    while status != 0 {
        status = status - 1;
        let v: i32 = bget(&ctx.arena, buffer + pos) as i8 as i32;
        ctx.emit(v);
        pos = pos + 1;
    }
    f.status = 0;
}

/// `mbfilter_htmlent.c:174-242`. ⚠⚠ `:178` is the FIRST read-back and it SIGN
/// EXTENDS; every access below is unchecked.
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
fn dec(ctx: &mut Ctx, f: &mut Filt, c: i32) {
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
            while pos < f.status {
                let d: i32 = bget(&ctx.arena, buffer + pos as usize) as i8 as i32;
                ent = (ent as u32).wrapping_mul(10)
                                  .wrapping_add((d - 0x30) as u32) as i32;
                pos = pos + 1;
            }
            ctx.emit(ent);
            f.status = 0;
        } else {
            let tbl: &[Ent] = ent_table();
            let mut i: usize = 0;
            while i < tbl.len() {
                if name_eq(ctx, buffer, tbl[i].name) {
                    ent = tbl[i].code;
                    break;
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
        if !is_entity_char(c) || f.status + 1 == HTML_ENC_BUFFER_SIZE
            || (c == 0x23 && f.status > 2)
        {
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

const SHIM_COUNTS: [u64; 3] = [2, 2, 0];

/// ⚠ `#[cfg_attr(slb_isolated, inline(never))]` IS NOT COSMETIC: without it
/// LLVM inlines `kernel` into the driver loop and `measure.py` reports
/// `kernel_exclusive_ir = None` for every Rust cell, so the row has no A1
/// statistic at all. The C side gets the same thing from `SLB_NOINLINE`.
#[cfg_attr(slb_isolated, inline(never))]
fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let place: u32 = rd32(win, 0) & 3;
    let order: u32 = rd32(win, 4) & 1;

    let mut ctx: Ctx = Ctx::new();
    let mut fa: Filt = Filt { status: 0, cache: 0 };
    let mut fb: Filt = Filt { status: 0, cache: 0 };
    dec_ctor(&mut ctx, &mut fa, (place & 1) as usize);
    dec_ctor(&mut ctx, &mut fb, ((place >> 1) & 1) as usize);

    let mut i: usize = HEAD;
    while i < len {
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
    let mut j: usize = 0;
    while j < 3 {
        acc = acc.wrapping_mul(31).wrapping_add(SHIM_COUNTS[j]);
        j = j + 1;
    }
    acc
}

fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;

    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
