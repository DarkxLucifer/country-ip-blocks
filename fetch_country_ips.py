

---

# fetch_country_ips.py
```python
#!/usr/bin/env python3
"""
fetch_country_ips.py

Fetch country IP blocks (CIDRs) for a given ISO2 country code.
Sources (in order):
 - ipdeny (http://www.ipdeny.com/)
 - ipinfo (https://ipinfo.io/) [fallback: free, limited rate; used without token]
Supports caching to ./cache/<COUNTRY>.cache

Outputs:
 - cidr  : one CIDR per line
 - ipset : ipset commands (create + add)
 - nftables : nftables set snippet

Example:
  python fetch_country_ips.py --country US --format cidr
"""

from __future__ import annotations
import argparse
import os
import time
import sys
from typing import List, Tuple
import requests

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
IPDENY_URL_TEMPLATE = "https://www.ipdeny.com/ipblocks/data/countries/{cc}.zone"
IPDENY_URL_TEMPLATE_V6 = "https://www.ipdeny.com/ipv6/ipaddresses/ip6-{cc}.txt"
IPINFO_URL = "https://ipinfo.io/countries/{cc}/cidr"  # not official; fallback patterns may vary

DEFAULT_TIMEOUT = 10
CACHE_TTL = 24 * 3600  # 24 hours by default

def ensure_cache_dir():
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

def cache_path(cc: str) -> str:
    ensure_cache_dir()
    return os.path.join(CACHE_DIR, f"{cc.lower()}.cache")

def read_cache(cc: str) -> Tuple[float, List[str]]:
    path = cache_path(cc)
    if not os.path.exists(path):
        return 0.0, []
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip()
        try:
            ts = float(header)
        except Exception:
            ts = 0.0
        lines = [l.strip() for l in f if l.strip()]
    return ts, lines

def write_cache(cc: str, cidrs: List[str]) -> None:
    path = cache_path(cc)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{time.time()}\n")
        for c in cidrs:
            f.write(c + "\n")

def fetch_from_ipdeny(cc: str) -> List[str]:
    # ipdeny provides IPv4 lists at {cc}.zone and IPv6 at ip6-{cc}.txt
    list_out = []
    cc = cc.lower()
    urls = [
        IPDENY_URL_TEMPLATE.format(cc=cc),
        IPDENY_URL_TEMPLATE_V6.format(cc=cc)
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=DEFAULT_TIMEOUT)
            if r.status_code == 200:
                # ipdeny returns plain CIDRs, one per line
                for line in r.text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    list_out.append(line)
        except Exception:
            # ignore and continue to other source
            pass
    return list_out

def fetch_from_ipinfo(cc: str) -> List[str]:
    # ipinfo has various endpoints; this is a fallback attempt using a common pattern.
    # NOTE: this endpoint may not exist on ipinfo. If a token is provided, a better API call can be used.
    url = IPINFO_URL.format(cc=cc.upper())
    out = []
    try:
        r = requests.get(url, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 200:
            for line in r.text.splitlines():
                s = line.strip()
                if s:
                    out.append(s)
    except Exception:
        pass
    return out

def dedupe_preserve_order(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def fetch_country_cidrs(cc: str, force_refresh: bool=False, ttl: int=CACHE_TTL) -> List[str]:
    cc = cc.strip().lower()
    if len(cc) != 2:
        raise ValueError("country code must be 2-letter ISO code, e.g. 'US', 'IN'")

    ts, cached = read_cache(cc)
    if not force_refresh and cached and (time.time() - ts) < ttl:
        return cached

    # try ipdeny first
    cidrs = fetch_from_ipdeny(cc)
    if not cidrs:
        cidrs = fetch_from_ipinfo(cc)

    # final fallback: try uppercase cc on ipdeny (some hosts prefer lowercase)
    if not cidrs:
        cidrs = fetch_from_ipdeny(cc.upper())

    cidrs = [c for c in cidrs if c and "/" in c]  # quick validation
    cidrs = dedupe_preserve_order(cidrs)
    if cidrs:
        write_cache(cc, cidrs)
    return cidrs

def format_ipset(cidrs: List[str], set_name: str="country-set") -> str:
    ipv4_set = f"{set_name}-v4"
    ipv6_set = f"{set_name}-v6"
    lines = []
    # create commands (safe: check existence)
    lines.append(f"ipset create {ipv4_set} hash:net family inet -exist")
    lines.append(f"ipset create {ipv6_set} hash:net family inet6 -exist")
    for c in cidrs:
        if ":" in c:
            lines.append(f"ipset add {ipv6_set} {c} -exist")
        else:
            lines.append(f"ipset add {ipv4_set} {c} -exist")
    return "\n".join(lines)

def format_nftables(cidrs: List[str], set_name: str="country_set") -> str:
    # create an nftables set in inet family 'filter'
    lines = []
    ipv4 = [c for c in cidrs if ":" not in c]
    ipv6 = [c for c in cidrs if ":" in c]
    if ipv4:
        lines.append(f"nft add set inet filter {set_name}_v4 {{ type ipv4_addr; flags interval; }}")
        block = ", ".join(ipv4)
        lines.append(f"nft add element inet filter {set_name}_v4 {{ {block} }}")
    if ipv6:
        lines.append(f"nft add set inet filter {set_name}_v6 {{ type ipv6_addr; flags interval; }}")
        block = ", ".join(ipv6)
        lines.append(f"nft add element inet filter {set_name}_v6 {{ {block} }}")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description="Fetch country IP CIDRs")
    p.add_argument("--country", "-c", required=True, help="ISO2 country code (e.g. US, IN)")
    p.add_argument("--format", "-f", choices=("cidr","ipset","nftables"), default="cidr", help="Output format")
    p.add_argument("--ipset-name", default=None, help="Name for ipset (for ipset format)")
    p.add_argument("--set-name", default=None, help="Name for nftables set (for nftables format)")
    p.add_argument("--no-cache", action="store_true", help="Ignore cache and force refresh")
    p.add_argument("--ttl", type=int, default=CACHE_TTL, help="Cache TTL in seconds (default 86400)")
    args = p.parse_args()

    try:
        cidrs = fetch_country_cidrs(args.country, force_refresh=args.no_cache, ttl=args.ttl)
    except ValueError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(2)

    if not cidrs:
        print(f"# No CIDRs found for country {args.country}", file=sys.stderr)
        sys.exit(1)

    if args.format == "cidr":
        for c in cidrs:
            print(c)
    elif args.format == "ipset":
        name = args.ipset_name or f"country-{args.country.upper()}"
        print(format_ipset(cidrs, set_name=name))
    elif args.format == "nftables":
        name = args.set_name or f"country_{args.country.upper()}"
        print(format_nftables(cidrs, set_name=name))
    else:
        for c in cidrs:
            print(c)

if __name__ == "__main__":
    main()
