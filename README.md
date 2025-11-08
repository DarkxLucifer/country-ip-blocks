# country-ip-fetcher

Small utility to fetch IPv4/IPv6 CIDR blocks for a given country (ISO 3166-1 alpha-2), with caching and multiple sources.

Features
- Fetches from configurable sources (ipdeny + ipinfo fallback).
- Outputs plain CIDR list, ipset commands, or nftables set snippet.
- Caches results to avoid frequent downloads.
- Optional GitHub Actions workflow to refresh lists daily and commit.

Usage
```bash
pip install -r requirements.txt
python fetch_country_ips.py --country US --format cidr > us.cidr
python fetch_country_ips.py --country IN --format ipset --ipset-name country-IN
python fetch_country_ips.py --country CN --format nftables --set-name country_CN
