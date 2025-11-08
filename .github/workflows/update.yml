#!/usr/bin/env python3
"""
fetch_country_ips.py - improved/debuggable

Usage examples:
  python fetch_country_ips.py --country US --format cidr > generated/us.cidr
  python fetch_country_ips.py --country US --format cidr --debug-out generated/us.debug
"""

from __future__ import annotations
import argparse
import os
import sys
import time
from typing import List
import requests

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
IPDENY_URL_IPV4 = "https://www.ipdeny.com/ipblocks/data/countries/{cc}.zone"
IPDENY_URL_IPV6 = "https://www.ipdeny.com/ipv6/ipaddresses/ip6-{cc}.txt"
# fallback source (may or may not exist) -- keep as emergency fallback
IPINFO_URL = "https://ipinfo.io/countries/{cc}/cidr"

DEFAULT_TIMEOUT = 10
CACHE_TTL = 24 * 3600

def ensure_cache_dir():
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def cache_path(cc: str) -> str:
    ensure_cache_dir()
    return os.path.join(CACHE_DIR, f"{cc.lower()}.cache")

def read_cache(cc: str):
    path = cache_path(cc)
    if not os.path.exists(path):
        return 0.0, []
    try:
        with open(path, "r", encoding="utf-8") as f:
            header = f.readline().strip()
            ts = float(header) if header else 0.0
            lines = [l.strip() for l in f if l.strip()]
        return ts, lines
    except Exception:
        return 0.0, []

def write_cache(cc: str, cidrs: List[str]) -> None:
    path = cache_path(cc)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{time.time()}\n")
        for c in cidrs:
            f.write(c + "\n")

def fetch_url(url: str, timeout=DEFAULT_TIMEOUT):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code, r.text
    except Exception as e:
        return None, f"ERROR: request failed: {e}"

def fetch_from_ipdeny(cc: str, debug_lines: List[str]) -> List[str]:
    cc_low = cc.lower()
    urls = [
        IPDENY_URL_IPV4.format(cc=cc_low),
        IPDENY_URL_IPV6.format(cc=cc_low)
    ]
    cidrs = []
    for u in urls:
        debug_lines.append(f"Trying ipdeny URL: {u}")
        status, text = fetch_url(u)
        debug_lines.append(f" -> status: {status}")
        if status == 200 and text:
            for line in text.splitlines():
                s = line.strip()
                if s and not s.startswith("#"):
                    cidrs.append(s)
        else:
            debug_lines.append(f" -> ipdeny returned no usable content for {u}")
    return cidrs

def fetch_from_ipinfo(cc: str, debug_lines: List[str]) -> List[str]:
    url = IPINFO_URL.format(cc=cc.upper())
    debug_lines.append(f"Trying ipinfo URL: {url}")
    status, text = fetch_url(url)
    debug_lines.append(f" -> status: {status}")
    cidrs = []
    if status == 200 and text:
        for line in text.splitlines():
            s = line.strip()
            if s:
                cidrs.append(s)
    else:
        debug_lines.append(" -> ipinfo returned no usable content")
    return cidrs

def dedupe_preserve_order(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def fetch_country_cidrs(cc: str, force_refresh: bool=False, ttl: int=CACHE_TTL, debug_lines: List[str]=None):
    if debug_lines is None:
        debug_lines = []
    cc = cc.strip().lower()
    if len(cc) != 2:
        raise ValueError("country code must be 2-letter ISO code (e.g. US, IN)")

    ts, cached = read_cache(cc)
    debug_lines.append(f"Cache stamp: {ts}, entries: {len(cached)}")
    if not force_refresh and cached and (time.time() - ts) < ttl:
        debug_lines.append("Using cached results")
        return cached

    # try ipdeny
    cidrs = fetch_from_ipdeny(cc, debug_lines)
    if not cidrs:
        debug_lines.append("ipdeny returned no cidrs; trying ipinfo fallback")
        cidrs = fetch_from_ipinfo(cc, debug_lines)

    # last-ditch: try uppercase ipdeny (some hosts are case-sensitive)
    if not cidrs:
        debug_lines.append("Trying ipdeny with uppercase country code")
        cidrs = []
        urls = [
            IPDENY_URL_IPV4.format(cc=cc.upper()),
            IPDENY_URL_IPV6.format(cc=cc.upper())
        ]
        for u in urls:
            debug_lines.append(f"Trying: {u}")
            status, text = fetch_url(u)
            debug_lines.append(f" -> status: {status}")
            if status == 200 and text:
                for line in text.splitlines():
                    s = line.strip()
                    if s and not s.startswith("#"):
                        cidrs.append(s)

    cidrs = [c for c in cidrs if c and "/" in c]
    cidrs = dedupe_preserve_order(cidrs)
    debug_lines.append(f"Total cidrs found: {len(cidrs)}")

    if cidrs:
        try:
            write_cache(cc, cidrs)
            debug_lines.append(f"Wrote cache: {cache_path(cc)}")
        except Exception as e:
            debug_lines.append(f"Failed to write cache: {e}")

    return cidrs

def format_cidr_output(cidrs):
    return "\n".join(cidrs)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--country", "-c", required=True)
    p.add_argument("--format", "-f", choices=("cidr",), default="cidr")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--ttl", type=int, default=CACHE_TTL)
    p.add_argument("--debug-out", default=None, help="path to write debug info")
    args = p.parse_args()

    debug_lines = []
    try:
        cidrs = fetch_country_cidrs(args.country, force_refresh=args.no_cache, ttl=args.ttl, debug_lines=debug_lines)
    except Exception as e:
        debug_lines.append(f"ERROR: exception: {e}")
        cidrs = []

    # write debug if requested
    if args.debug_out:
        try:
            with open(args.debug_out, "w", encoding="utf-8") as f:
                f.write("\n".join(debug_lines))
        except Exception:
            pass

    if not cidrs:
        # print a human-readable commented error so generated file is never totally blank
        sys.stderr.write("ERROR: no CIDRs found for country {}\n".format(args.country))
        # Print a comment to stdout so the generated file explicitly contains diagnostics
        print("# ERROR: no CIDRs found for country {}".format(args.country))
        for ln in debug_lines:
            print("# DBG: " + (ln if isinstance(ln, str) else repr(ln)))
        # exit non-zero so CI can detect failure if desired
        sys.exit(2)

    # success: print CIDRs
    if args.format == "cidr":
        print(format_cidr_output(cidrs))
    else:
        print(format_cidr_output(cidrs))

if __name__ == "__main__":
    main()
