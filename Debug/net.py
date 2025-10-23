#!/usr/bin/env python3
"""
Windows network monitor (passive): logs all TCP/UDP connections (IPv4/IPv6)
without interacting with any specific game/process. Suitable for running
alongside games with anti-cheat because it only uses OS APIs (psutil) and
optional DNS lookups. No packet sniffing, no drivers.

Outputs JSON lines with details: timestamp, event (open/close/status_change),
proto, family, local/remote endpoints, pid, process name, and optional rDNS.

Recommended to run with Administrator privileges to see system-wide connections.
"""

import argparse
import ipaddress
import json
import os
import platform
import socket
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
try:
    import msvcrt  # Windows console keyboard
    HAS_MSVCRT = True
except Exception:
    HAS_MSVCRT = False

try:
    import psutil  # type: ignore
except Exception as e:
    print("psutil is required. Install with: pip install psutil", file=sys.stderr)
    raise

# Optional DNS resolver via dnspython (faster/more controllable timeouts than socket.gethostbyaddr)
try:
    import dns.resolver  # type: ignore
    import dns.reversename  # type: ignore
    HAS_DNSPYTHON = True
except Exception:
    HAS_DNSPYTHON = False


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def family_to_str(fam: int) -> str:
    try:
        if fam == socket.AF_INET:
            return "ipv4"
        if fam == socket.AF_INET6:
            return "ipv6"
    except Exception:
        pass
    return str(fam)


def type_to_str(typ: int) -> str:
    try:
        if typ == socket.SOCK_STREAM:
            return "tcp"
        if typ == socket.SOCK_DGRAM:
            return "udp"
    except Exception:
        pass
    return str(typ)


def safe_proc_info(pid: Optional[int]) -> Dict[str, Optional[str]]:
    info = {"pid": pid, "name": None, "exe": None}
    if pid is None or pid < 0:
        return info
    try:
        p = psutil.Process(pid)
        info["name"] = safe_get(lambda: p.name())
        info["exe"] = safe_get(lambda: p.exe())
    except Exception:
        pass
    return info


def safe_get(fn):
    try:
        return fn()
    except Exception:
        return None


class ReverseDNS:
    def __init__(self, enable: bool = True, timeout: float = 0.8):
        self.enable = enable
        self.timeout = timeout
        self._cache: Dict[str, Optional[str]] = {}
        self._lock = threading.Lock()
        if HAS_DNSPYTHON:
            self.resolver = dns.resolver.Resolver(configure=True)
            self.resolver.timeout = timeout
            self.resolver.lifetime = timeout
        else:
            self.resolver = None

    def lookup(self, ip: str) -> Optional[str]:
        if not self.enable:
            return None

        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return None
        except Exception:
            return None

        with self._lock:
            if ip in self._cache:
                return self._cache[ip]

        name: Optional[str] = None
        try:
            if HAS_DNSPYTHON and self.resolver is not None:
                rr = dns.reversename.from_address(ip)
                ans = self.resolver.resolve(rr, "PTR")
                if ans and len(ans) > 0:
                    name = str(ans[0]).rstrip(".")
            else:
                # Basic fallback
                old_timeout = socket.getdefaulttimeout()
                try:
                    socket.setdefaulttimeout(self.timeout)
                    name = socket.gethostbyaddr(ip)[0]
                finally:
                    socket.setdefaulttimeout(old_timeout)
        except Exception:
            name = None

        with self._lock:
            self._cache[ip] = name
        return name


def write_jsonl(fp, obj: dict):
    fp.write(json.dumps(obj, ensure_ascii=False) + "\n")
    fp.flush()


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Log all network connections to JSONL.")
    ap.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds (default: 1.0)")
    ap.add_argument("--log", type=str, default=None, help="Output JSONL file path (default: ./netlog_YYYYmmdd_HHMMSS.jsonl)")
    ap.add_argument("--no-dns", action="store_true", help="Disable reverse DNS lookups")
    ap.add_argument("--dns-timeout", type=float, default=0.8, help="Reverse DNS timeout per query (default: 0.8s)")
    ap.add_argument("--tcp-only", action="store_true", help="Log only TCP connections")
    ap.add_argument("--udp-only", action="store_true", help="Log only UDP connections")
    ap.add_argument("--log-duplicates", action="store_true", help="Also log duplicates each poll (not only changes)")
    ap.add_argument("--no-close-events", action="store_true", help="Do not log close events when connections disappear")
    # Marker hotkeys
    ap.add_argument("--markers", action="store_true", help="Enable hotkeys: F1 marker1, F2 marker2 (Windows console)")
    ap.add_argument("--marker1", type=str, default="matchmaking_start", help="Label for F1 marker (default: matchmaking_start)")
    ap.add_argument("--marker2", type=str, default="issue_observed", help="Label for F2 marker (default: issue_observed)")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.tcp_only and args.udp_only:
        print("Choose at most one of --tcp-only or --udp-only", file=sys.stderr)
        return 2

    if platform.system() != "Windows":
        print("Warning: this monitor is designed for Windows; running on: " + platform.system(), file=sys.stderr)

    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.log:
        out_path = Path(args.log)
    else:
        out_path = out_dir / f"netlog_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"

    rdns = ReverseDNS(enable=not args.no_dns, timeout=args.dns_timeout)

    # Track connections we've already logged to avoid constant duplicates
    # Key: (pid, fam, typ, l_ip, l_port, r_ip, r_port)
    seen: Dict[Tuple, Dict[str, Optional[str]]] = {}

    # Prepare marker queue (from hotkey thread)
    marker_queue = []  # list of dicts to write
    mlock = threading.Lock()
    stop_event = threading.Event()

    def enqueue_marker(kind: str, label: str):
        with mlock:
            marker_queue.append({
                "ts": now_iso(),
                "event": "marker",
                "marker": kind,
                "label": label,
            })

    def kb_loop():
        if not HAS_MSVCRT:
            return
        # Inform user about keys
        print("Markers enabled: press F1/F2 in this console to add markers.")
        while not stop_event.is_set():
            try:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ('\x00', '\xe0'):
                        ch2 = msvcrt.getwch()
                        code = ord(ch2) if ch2 else -1
                        if code == 59:  # F1
                            enqueue_marker("F1", args.marker1)
                            print(f"[marker] F1 -> {args.marker1}")
                        elif code == 60:  # F2
                            enqueue_marker("F2", args.marker2)
                            print(f"[marker] F2 -> {args.marker2}")
                else:
                    time.sleep(0.05)
            except Exception:
                time.sleep(0.1)

    kb_thread = None
    if args.markers and platform.system() == "Windows" and HAS_MSVCRT:
        kb_thread = threading.Thread(target=kb_loop, name="kb_markers", daemon=True)
        kb_thread.start()

    # Open output
    with open(out_path, "a", encoding="utf-8") as fp:
        # Write a header/marker
        write_jsonl(fp, {
            "ts": now_iso(),
            "event": "start",
            "host": platform.node(),
            "platform": platform.platform(),
            "admin_note": "Run as Administrator to see system-wide connections.",
            "dns_enabled": not args.no_dns,
            "interval": args.interval,
            "markers": bool(args.markers),
            "marker1": args.marker1,
            "marker2": args.marker2,
        })

        try:
            while True:
                t0 = time.time()

                try:
                    conns = psutil.net_connections(kind="inet")
                except Exception as e:
                    # On some systems, querying all can fail; retry next tick
                    write_jsonl(fp, {"ts": now_iso(), "event": "error", "stage": "net_connections", "error": str(e)})
                    time.sleep(args.interval)
                    continue

                current_keys = set()

                # Flush marker queue first on each tick
                if args.markers:
                    with mlock:
                        pending = list(marker_queue)
                        marker_queue.clear()
                    for mk in pending:
                        write_jsonl(fp, mk)

                for c in conns:
                    fam = family_to_str(c.family)
                    typ = type_to_str(c.type)

                    if args.tcp_only and typ != "tcp":
                        continue
                    if args.udp_only and typ != "udp":
                        continue

                    l_ip = getattr(c.laddr, 'ip', None) or (c.laddr[0] if c.laddr else None)
                    l_port = getattr(c.laddr, 'port', None) or (c.laddr[1] if c.laddr else None)
                    if not l_ip:
                        continue  # skip invalid entries

                    r_ip = None
                    r_port = None
                    if c.raddr:
                        r_ip = getattr(c.raddr, 'ip', None) or (c.raddr[0] if isinstance(c.raddr, tuple) and len(c.raddr) > 0 else None)
                        r_port = getattr(c.raddr, 'port', None) or (c.raddr[1] if isinstance(c.raddr, tuple) and len(c.raddr) > 1 else None)

                    key = (c.pid, fam, typ, l_ip, l_port, r_ip, r_port)
                    current_keys.add(key)

                    proc = safe_proc_info(c.pid)

                    status = c.status if hasattr(c, 'status') else None

                    first_seen = key not in seen
                    status_changed = False
                    if not first_seen:
                        prev = seen.get(key, {})
                        if prev.get("status") != status:
                            status_changed = True

                    if first_seen or status_changed or args.log_duplicates:
                        entry = {
                            "ts": now_iso(),
                            "event": "open" if first_seen else ("status_change" if status_changed else "sample"),
                            "family": fam,
                            "proto": typ,
                            "status": status,
                            "laddr": {"ip": l_ip, "port": l_port},
                            "raddr": {"ip": r_ip, "port": r_port} if r_ip else None,
                            "pid": proc["pid"],
                            "process": {"name": proc["name"], "exe": proc["exe"]},
                        }

                        if r_ip:
                            rdns_name = rdns.lookup(r_ip)
                            if rdns_name:
                                entry["rdns"] = rdns_name

                        write_jsonl(fp, entry)

                    # Update seen
                    seen[key] = {"status": status}

                # Emit close events for disappeared connections
                if not args.no_close_events:
                    disappeared = [k for k in list(seen.keys()) if k not in current_keys]
                    for k in disappeared:
                        pid, fam, typ, l_ip, l_port, r_ip, r_port = k
                        entry = {
                            "ts": now_iso(),
                            "event": "close",
                            "family": fam,
                            "proto": typ,
                            "laddr": {"ip": l_ip, "port": l_port},
                            "raddr": {"ip": r_ip, "port": r_port} if r_ip else None,
                            "pid": pid,
                        }
                        write_jsonl(fp, entry)
                        del seen[k]

                # Sleep remaining time
                elapsed = time.time() - t0
                to_sleep = max(0.0, args.interval - elapsed)
                time.sleep(to_sleep)

        except KeyboardInterrupt:
            write_jsonl(fp, {"ts": now_iso(), "event": "stop", "reason": "KeyboardInterrupt"})

    print(f"Log written to: {out_path}")
    print("Tip: Run the script as Administrator to capture all processes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
