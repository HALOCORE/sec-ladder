# TASK_PHP_002 — Phase 0: the foundation

**Role:** research engineer. **One agent, working alone.**
**Report:** `.tasks-php/TASK_PHP_002_REPORT.md` — ⚠ **write the file, do not
leave it in your return message** (`PROTOCOL.md` rule 10).

Read `.tasks/PROTOCOL.md` first (it is reused unchanged), then `PLAN_PHP.md`
§1–§4 and §7, then `.tasks-php/README.md`. `RECAP_PHP.md` is the live state.

**You are building infrastructure, not patterns.** No PHP kernel is extracted in
this task. The deliverable is a pipeline that a later task can point at a real
row, plus the evidence that it did not disturb the PAT programme.

---

## §0 The constraint that shapes everything

⚠⚠⚠ **DO NOT EDIT ANY FILE UNDER `harness/`, `common/`, `patterns/`, `results/`
or `pilot/`.** `harness/*.py` and `common/*.py` are hashed into all 33 PAT gate
records; `harness/{build,asm,measure}.py` into all 33 measurement records.
Adding one `.py` to either directory costs a 33-pattern re-gate; editing
`build.py` costs a full re-measure. `PLAN_PHP.md` §2.1 has the globs.

**Your first and last command, both pasted into the report:**

```sh
python3 harness/measure.py --check-stale      # must print: 66 record(s) examined, 0 STALE
```

⚠ 66 is gate **plus** measurement records. A commit message has already misread
that as measurement records alone.

---

## §1 Deliverables

### 1. `patterns-php/SOURCES.md` + the manifest

The pristine PHP 5.0.0 tarball lives under **another project's gitignored
`.temp/`** and is deletable at any time. Nothing may cite it until it can be
re-identified without it.

- `patterns-php/SOURCES.md` — the tarball's sha256
  (`5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919`), size
  (5595997), entry count (3815), provenance URL (`museum.php.net`), the
  `tar -xzOf … | sed -n` read recipe, and **the rule that every citation in this
  programme resolves against this tarball and never against a build tree**
  (every extracted tree on this box is patched — modern-gcc, and two of them the
  allocator).
- `patterns-php/php-5.0.0.manifest` — sha256 of **every `.c` and `.h`** in the
  tarball, **tarball-relative paths**, one header line naming the root. Model it
  on `common/census/php.manifest` and read its `README.md` §1 first: paths are
  corpus-relative because that alone took a comparable manifest 950 K → 506 K
  with zero content lost, and gzip was measured and **rejected** for stopping
  being greppable and diffable.
- `patterns-php/manifest.sh` — the regenerator. **Read-only on the tarball.**

✅ **Report the file count and total size.** If the manifest exceeds ~600 K, say
so and justify keeping it against `.memory/00-environment.md`'s *"kilobytes, not
gigabytes"*, the way `common/census/README.md` does — do not silently ship it.

### 2. `harness-php/root.py` — the symlink shim

Builds `.temp/php-root/`, the directory the unmodified PAT gate is run out of.
The mechanism and the evidence for it are in `PLAN_PHP.md` §2.1a; **re-derive it
yourself rather than trusting that section.**

```
.temp/php-root/harness      -> ../../harness        (real, unmodified)
.temp/php-root/common       -> ../../common-php
.temp/php-root/patterns     -> ../../patterns-php
.temp/php-root/results      -> ../../results-php
.temp/php-root/verus_run.py -> ../../verus_run.py
```

⚠⚠ **THAT LIST IS INCOMPLETE AND I KNOW OF ONE GAP — FIND THE REST.**
`harness/build.py:50` sets `BUILD_ROOT = os.path.join(REPO, ".temp", "build")`.
Through the shim that becomes `.temp/php-root/.temp/build`, a nested scratch
tree. Decide whether the shim gets its own `.temp` symlink or its own build
root, **and say which and why.** Then **enumerate every other `REPO`-relative
path the four modules construct** (`build.py`, `check.py`, `measure.py`,
`report.py`) and confirm each one lands somewhere correct. Do not assume the
five links above are sufficient — I listed them from four modules' constants,
not from a sweep.

The shim is a **derived artefact**: gitignored, rebuilt by this script. Keep the
generator, delete the artefact.

### 3. `harness-php/gate.py` — the driver

Runs the unmodified `harness/check.py` (and `measure.py`, `report.py`) through
the shim, for a named php pattern. Thin: build the shim, exec the real tool,
surface its exit code. **It must not reimplement any gate stage.**

### 4. `common-php/`

- `emalloc_shim.{c,h}` — faithful to `Zend/zend_alloc.c`'s `_emalloc`, **every
  line cited to the pristine tarball**, reproducing **BOTH truncations**:
  `zend_alloc.c:129`'s `unsigned int real_size` **and** — found by the spatial
  miner after this spec's first draft, ✅ manager-verified —
  **`zend_alloc.h:53`'s `unsigned int size:31`, the 31-bit bitfield the
  *recorded* size is stored in.** ⚠ Note that `_safe_emalloc` checks in 64-bit
  `long` and **then calls the truncating `_emalloc`**, so it protects against
  neither; a shim that models only `_safe_emalloc` is not faithful. This is not optional: substituting plain `malloc`
  once made an earlier effort report a real defect as unreachable *and* invent
  an explanation for the upstream fix (`PLAN_PHP.md` §4.3). Ship a probe that
  **demonstrates the truncation firing** — an 18-exabyte request becoming a
  ~2 GiB allocation that succeeds — with a **must-fire positive control**.
- Re-exports of the PAT `common/driver.{c,h,rs}` and `slb.py` the php side
  reuses, so the shim's `common → common-php` link resolves them.

⚠⚠ **THE THING TO GET RIGHT, AND IT IS THE ONE I EXPECT TO BE HARDEST:** verify
that **nothing under `common-php/` ends up in no digest at all**. `check.py`'s
`srcs` globs `common/`, so under the shim your files land under the key
`common/…` in php records — *if* the link is arranged correctly. Prove it by
listing the `source_sha256` keys of an actual php gate record and showing every
`common-php/` file present. ⚠ Ten committed control sources sat in no digest on
the PAT side for many tasks; that is the failure this check exists for.

### 5. `.tasks-php/PROTOCOL_PHP.md` — an ADDENDUM, not a fork

Only what is new: extraction tiers (`verbatim`/`narrowed`/`modelled`), the
deletion ledger, reachability-settled-first, the allocator rule, R1h = the real
`fix_commit`, fidelity evidence, and the `provenance` block. **Do not restate
anything already in `.tasks/PROTOCOL.md`** — two copies of one rule is how both
go stale.

### 6. The `provenance` block

Implement `PLAN_PHP.md` §6 as a validator: given a `patterns-php/*/spec.md`,
check that `provenance.extract_sha256` equals the sha256 of the bytes the
recorded `extract_cmd` actually produces from the pinned tarball. **This is the
field that makes "this kernel came from those lines" a one-command check rather
than a claim.** ⚠ Give it a **must-fire negative test** — a deliberately wrong
line span that the validator rejects. A validator with no failing case is a
validator nobody has tested.

### 7. `ph00-smoke` — the end-to-end proof

The pipeline is unproven until a gate has actually run green through the shim
and written to `results-php/`. Relocate the **known-green** `p01` kernel as
`patterns-php/ph00-smoke/`.

- It is **throwaway**, prices nothing, carries **no security claim** and **no
  PHP provenance**. Its `provenance` block must say so in terms, so that nobody
  ever mistakes it for a php row.
- ⚠ You may **copy** from `patterns/p01-array-sum/` but must not **edit** it.
- ⚠ Its `spec.md` `why` must be rewritten to ≤ 200 words (`RECAP_PHP.md`'s size
  rule). Do **not** carry over p01's ~7,000-word JSON string.

**Acceptance:** `harness-php/gate.py ph00` is green, and the record lands in
`results-php/gate/`.

---

## §2 The must-fire tests

A green run is evidence about the check. For each of these, **state what would
make it fail, then show it passing**:

| # | test | must show |
|---|---|---|
| T1 | `measure.py --check-stale` before **and** after the whole task | `66 examined, 0 STALE` both times |
| T2 | shim digest fidelity | recompute `p01`'s gate `source_sha256` through the shim, diff against the **committed** `results/gate/p01-array-sum.json`: identical keys **and** hashes |
| T3 | **no write escapes the php tree** | run the full `ph00` gate, then show `git status --short` touches nothing under `patterns/`, `results/`, `harness/`, `common/`, `pilot/`. ⚠ Take a **before** snapshot; a clean `git status` after a run that wrote nothing proves nothing about a run that would have |
| T4 | `common-php/` is hashed | every `common-php/` file appears in `ph00`'s gate `source_sha256` |
| T5 | provenance validator | one passing case **and** one deliberately-wrong span that it rejects |
| T6 | emalloc truncation | the 18-EiB → ~2 GiB success, **plus** a positive control that must also fire |

⚠ **`env -u LD_PRELOAD` for any hand-run sanitizer probe.** This shell inherits
`LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so`; a dynamically linked ASan
binary refuses to start behind it **and still exits 1**, so an exit-code check
cannot tell "blind" from "found nothing". Grep for `AddressSanitizer`, not
`ASan`. (`harness/check.py` uses `-static-libasan` and is unaffected.)

---

## §3 Rules

- Scratch under `.temp/php0/`. **Never `/tmp`.** Keep the generator, delete the
  artefact — but ⚠ **anything a record CITES is evidence and does not get
  deleted.**
- **No `git add` / `git commit`.** Read-only git is fine. The manager commits.
- `timeout <N> <cmd>` on anything long.
- **Everything you claim must have been RUN with the output pasted.** "Should
  work" is not done.
- Do not widen scope. If you see adjacent work, report it.

---

## §4 The calls I am least sure of — please refute them

`PROTOCOL.md` rule 2. Every agent that has contradicted the manager with a
measurement has been right. Three, by name:

1. ⚠ **"The symlink shim needs only the five links in §2, plus a decision about
   `.temp`."** I derived that from four modules' constants, **not** from a
   sweep. I expect you to find at least one more `REPO`-relative path that
   misbehaves. **Sweep it properly and tell me what I missed.**
2. ⚠ **"Relocating `p01` as `ph00-smoke` is the cheapest end-to-end proof."** It
   may drag PAT-specific pins (obligation counts, identity levels, the `Ir`
   floor, Miri policy) that make it *more* work than a minimal fresh kernel. If
   so, **build the minimal one instead** and say why.
3. ⚠ **"`common-php/` re-exporting the PAT `common/` files via symlink will hash
   correctly."** I verified the *harness* half of the digest through the shim; I
   did **not** verify the `common/` half, and symlinked directories inside a
   globbed path are exactly where I would expect this to break.

If any of the three is wrong, **the measurement wins and the plan gets
corrected**, not the other way round.

---

**Running count for this programme: launched from 4.** `TASK_PHP_001`'s three
miners each refuted the manager claim they were named to attack, and one of them
additionally corrected a manager error that had reached all three prompts (the
*"123 ASan reports"* figure).
It is a rigour signal, not a ledger; never add it to the PAT programme's ≈965.
**Reconciliation is the manager's job, not yours** — state in your report the
figure you were launched from and what you refuted, and let the manager carry it
forward.
