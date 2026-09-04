#!/usr/bin/env python3
"""index.stdio.py — the sec-ladder report's tiny backend (line-delimited JSON-RPC).

The report is a static site: `data/` is pre-built and the page works with no
backend at all.  This service exists for one thing — **rebuilding `data/` from
the repository without leaving the browser**, so the page can be refreshed after
a new pattern lands.

WRITES ONLY UNDER `.web/`.  `rebuild` shells out to `.web/build_data.py`, whose
only writer refuses any path outside this directory.  `doc` reads repository
files and never writes.  Nothing here mutates the research tree.

PROTOCOL
========
One JSON-RPC request per stdin line, one JSON response per stdout line; the web
layer wraps them in a {"kind":"JSON_LIST","data":[...]} envelope.

METHODS
=======
  help()                      -> {text}     this docstring
  list_methods()              -> {methods:[{name, doc}]}
  echo(params)                -> {params}   liveness check
  status()                    -> {fresh, built_utc, newest_evidence, patterns}
  rebuild()                   -> {ok, stdout, seconds}   runs build_data.py
  doc(path)                   -> {text, bytes}  read one repo text file (read-only)

ERROR CODES
===========
  -32700 parse · -32600 invalid request · -32601 no such method
  -32602 invalid params · -32603 internal
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional

_MODULE_HELP = __doc__

WEB = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(WEB)

PARSE_ERROR, INVALID_REQUEST = -32700, -32600
METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL = -32601, -32602, -32603

# `doc` may read these, and only these, and only under the repository root.
DOC_SUFFIXES = (".md", ".rs", ".c", ".h", ".py", ".json", ".toml", ".txt")
DOC_MAX_BYTES = 2_000_000


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        super().__init__(message)
        self.code, self.message, self.data = code, message, data


# ==================== methods ====================

def m_help(params: Dict[str, Any]) -> Dict[str, Any]:
    return {"text": _MODULE_HELP}


def m_list_methods(params: Dict[str, Any]) -> Dict[str, Any]:
    return {"methods": [{"name": n, "doc": (f.__doc__ or "").strip().splitlines()[0] if f.__doc__ else ""}
                        for n, f in METHODS.items()]}


def m_echo(params: Dict[str, Any]) -> Dict[str, Any]:
    """Echo params back unchanged."""
    return {"params": params}


def _newest_evidence() -> Dict[str, Any]:
    newest, path = 0.0, None
    for pat in ("results/*.json", "results/gate/*.json", "patterns/*/*.rs",
                "patterns/*/c/*.c", "patterns/*/spec.md", "patterns/*/NOTES.md"):
        for f in glob.glob(os.path.join(REPO, pat)):
            m = os.path.getmtime(f)
            if m > newest:
                newest, path = m, f
    return {"mtime": newest, "file": os.path.relpath(path, REPO) if path else None}


def m_status(params: Dict[str, Any]) -> Dict[str, Any]:
    """Is data/ older than the evidence it was built from?"""
    idx = os.path.join(WEB, "data", "index.json")
    built = os.path.getmtime(idx) if os.path.exists(idx) else 0.0
    ev = _newest_evidence()
    meta = {}
    if os.path.exists(idx):
        with open(idx, encoding="utf-8") as fh:
            d = json.load(fh)
        meta = {"built_utc": d.get("built_utc"), "patterns": len(d.get("patterns", [])),
                "head": (d.get("head") or {}).get("short")}
    return {"fresh": built >= ev["mtime"], "data_mtime": built,
            "newest_evidence": ev, **meta}


def m_rebuild(params: Dict[str, Any]) -> Dict[str, Any]:
    """Re-run .web/build_data.py (writes only under .web/)."""
    t0 = time.time()
    proc = subprocess.run([sys.executable, os.path.join(WEB, "build_data.py")],
                          capture_output=True, text=True, timeout=600, cwd=WEB)
    return {"ok": proc.returncode == 0, "returncode": proc.returncode,
            "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
            "seconds": round(time.time() - t0, 2)}


def m_doc(params: Dict[str, Any]) -> Dict[str, Any]:
    """Read one repository text file (read-only, whitelisted suffixes)."""
    rel = params.get("path")
    if not isinstance(rel, str) or not rel:
        raise RpcError(INVALID_PARAMS, "'path' must be a non-empty string")
    full = os.path.abspath(os.path.join(REPO, rel))
    if os.path.commonpath([full, REPO]) != REPO:
        raise RpcError(INVALID_PARAMS, "path escapes the repository")
    if not full.endswith(DOC_SUFFIXES):
        raise RpcError(INVALID_PARAMS, f"suffix not allowed; one of {DOC_SUFFIXES}")
    if not os.path.exists(full):
        raise RpcError(INVALID_PARAMS, f"no such file: {rel}")
    if os.path.getsize(full) > DOC_MAX_BYTES:
        raise RpcError(INVALID_PARAMS, "file too large")
    with open(full, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return {"text": text, "bytes": len(text), "path": rel}


METHODS = {
    "help": m_help,
    "list_methods": m_list_methods,
    "echo": m_echo,
    "status": m_status,
    "rebuild": m_rebuild,
    "doc": m_doc,
}


# ==================== dispatch ====================

def _err(rid, code, message, data=None):
    e = {"code": code, "message": message}
    if data is not None:
        e["data"] = data
    return {"jsonrpc": "2.0", "id": rid, "error": e}


def handle_one(req: Any) -> Dict[str, Any]:
    if not isinstance(req, dict):
        return _err(None, INVALID_REQUEST, "request must be an object")
    rid, method = req.get("id"), req.get("method")
    params = req.get("params") or {}
    if not isinstance(params, dict):
        return _err(rid, INVALID_PARAMS, "params must be an object")
    try:
        if method not in METHODS:
            raise RpcError(METHOD_NOT_FOUND, f"method not found: {method}")
        return {"jsonrpc": "2.0", "id": rid, "result": METHODS[method](params)}
    except RpcError as e:
        return _err(rid, e.code, e.message, e.data)
    except Exception as e:  # noqa: BLE001
        return _err(rid, INTERNAL, f"{type(e).__name__}: {e}")


def process_line(line: str) -> Any:
    try:
        req = json.loads(line)
    except json.JSONDecodeError as e:
        return _err(None, PARSE_ERROR, f"parse error: {e}")
    if isinstance(req, list):
        return [handle_one(r) for r in req] or _err(None, INVALID_REQUEST, "empty batch")
    return handle_one(req)


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            sys.stdout.write(json.dumps(process_line(line), ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except BrokenPipeError:
            break


if __name__ == "__main__":
    main()
