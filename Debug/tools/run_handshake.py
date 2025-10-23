#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "bin"
LISTS = ROOT / "lists"

def read_range() -> tuple[int,int]:
    p = (LISTS / "port-bf.txt")
    try:
        s = p.read_text(encoding="utf-8").strip()
    except Exception:
        s = "65530-65535"
    if not s:
        s = "65530-65535"
    if "-" in s:
        a,b = s.split("-",1)
        return int(a), int(b)
    v = int(s)
    return v, v

def build_wf(tmp: Path, start: int, end: int) -> None:
    expr = f"outbound and ((udp and (udp.SrcPort>={start} and udp.SrcPort<={end})) or (tcp and tcp.DstPort == 443))"
    tmp.write_text(expr, encoding="ascii")

def main() -> int:
    start, end = read_range()
    tmp = Path(os.getenv("TEMP") or os.getenv("TMP") or ".") / "wf_bf_handshake.txt"
    build_wf(tmp, start, end)
    winws = BIN / "winws.exe"
    if not winws.exists():
        print("winws.exe not found in bin/", file=sys.stderr)
        return 2
    args = [str(winws), f"--wf-raw=@{tmp}",
            "--filter-tcp=443", "--dpi-desync=fake,split2", "--dpi-desync-autottl=2", "--dpi-desync-repeats=6", "--dpi-desync-fooling=badseq", "--dpi-desync-badseq-increment=2", "--dpi-desync-cutoff=n2",
            "--new",
            "--filter-udp=*", "--dpi-desync=fake", "--dpi-desync-any-protocol=1", "--dpi-desync-autottl=2", "--dpi-desync-repeats=9", f"--dpi-desync-fake-unknown-udp={BIN / 'quic_initial_www_google_com.bin'}", "--dpi-desync-cutoff=n2"
            ]
    # Launch detached to avoid blocking
    DETACHED_PROCESS = 0x00000008
    try:
        subprocess.Popen(args, cwd=str(BIN), creationflags=DETACHED_PROCESS)
        print("Launched winws.exe with", tmp)
        return 0
    except Exception as e:
        print("Failed to launch winws:", e, file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

