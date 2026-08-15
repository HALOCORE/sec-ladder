//! sec-ladder shared Rust driver helpers -- the line-for-line mirror of
//! common/driver.c.
//!
//! What lives here: reading the input file (`.memory/02-bench-rules.md` format),
//! decoding the payload, and printing the checksum. What deliberately does NOT
//! live here: the driver *loop*. Rung 5's loop must sit inside `verus!` so the
//! kernel call site is verified (`.memory/02-bench-rules.md`, rule 2), and a
//! shared loop cannot be both plain Rust and Verus. So every rung carries its
//! own copy of the loop between `SLB-DRIVER-BEGIN` / `SLB-DRIVER-END` markers
//! and `harness/check.py` diffs the copies.
//!
//! Pulled in with `#[path = "../../common/driver.rs"] mod driver;`. In
//! `verus.rs` that `mod` sits outside `verus! { .. }`, so Verus treats it as
//! external (external-by-default); `verus.rs` reaches it through one small
//! `#[verifier::external_body]` wrapper whose TCB cost is tallied in NOTES.md.
//!
//! Exit codes and stderr text are part of the contract: the `adversarial`
//! inputs compare rung behaviour, so a divergence here would look like a
//! finding when it is really a driver bug.

#![allow(dead_code)]

use std::io::Read;

pub const EXIT_USAGE: i32 = 2;
pub const EXIT_OPEN: i32 = 3;
pub const EXIT_HEADER: i32 = 4;
pub const EXIT_TRUNCATED: i32 = 5;

pub struct Input {
    pub n_iters: u64,
    pub payload_len: u64,
    pub payload: Vec<u8>,
}

fn die(code: i32, msg: &str) -> ! {
    eprintln!("{}", msg);
    std::process::exit(code)
}

fn le64(b: &[u8]) -> u64 {
    let mut w = [0u8; 8];
    w.copy_from_slice(&b[..8]);
    u64::from_le_bytes(w)
}

/// argv[1], or exit(EXIT_USAGE).
pub fn arg_path() -> String {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        let prog = args.first().cloned().unwrap_or_else(|| "prog".to_string());
        die(EXIT_USAGE, &format!("usage: {} <input-file>", prog));
    }
    args[1].clone()
}

/// Read `path`, or exit with one of the codes above.
pub fn load(path: &str) -> Input {
    let mut f = match std::fs::File::open(path) {
        Ok(f) => f,
        Err(_) => die(EXIT_OPEN, &format!("slb: cannot open {}", path)),
    };
    let mut header = [0u8; 16];
    if f.read_exact(&mut header).is_err() {
        die(EXIT_HEADER, &format!("slb: {}: short header", path));
    }
    let n_iters = le64(&header[0..8]);
    let payload_len = le64(&header[8..16]);

    // Read exactly payload_len bytes and insist they were all there: this is the
    // "length field larger than the payload" adversarial case.
    let mut payload = Vec::new();
    if payload_len > 0 {
        let want = payload_len as usize;
        if want as u64 != payload_len {
            die(
                EXIT_TRUNCATED,
                &format!("slb: {}: payload_len {} exceeds usize", path, payload_len),
            );
        }
        // read_to_end rather than a `want`-sized zeroed buffer: allocating on an
        // attacker-controlled length would let adversarial-shortlen OOM us
        // before we ever get to reject it.
        if f.read_to_end(&mut payload).is_err() || payload.len() < want {
            die(
                EXIT_TRUNCATED,
                &format!("slb: {}: payload_len {} exceeds file size", path, payload_len),
            );
        }
        payload.truncate(want);
    }
    Input { n_iters, payload_len, payload }
}

/// Decode a byte payload as little-endian u64s, ignoring a trailing partial word.
/// Mirrors `slb_u64s` in common/driver.c and `slb.u64s` in common/slb.py.
pub fn le_u64s(payload: &[u8]) -> Vec<u64> {
    let n = payload.len() / 8;
    let mut v = Vec::with_capacity(n);
    for i in 0..n {
        v.push(le64(&payload[8 * i..8 * i + 8]));
    }
    v
}

/// Split the payload into (head word, remaining words). Mirrors
/// `slb_head_u64_body` in common/driver.c. An empty payload yields (0, vec![]).
pub fn head_u64_body(input: &Input) -> (u64, Vec<u64>) {
    let mut w = le_u64s(&input.payload);
    if w.is_empty() {
        return (0, Vec::new());
    }
    let head = w[0];
    w.remove(0);
    (head, w)
}

/// Print the checksum as a decimal u64 and a newline. Nothing else on stdout.
pub fn emit(acc: u64) {
    println!("{}", acc);
}
