import requests
import ipaddress
from pathlib import Path
from collections import defaultdict

URLS = [
    "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    "https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-latest",
    "https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest",
    "https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest",
    "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest",
]

OUT_DIR = Path("country")
OUT_DIR.mkdir(exist_ok=True)

countries = defaultdict(list)

for url in URLS:
    print(f"Downloading {url}")
    data = requests.get(url, timeout=60).text

    for line in data.splitlines():
        if line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < 7:
            continue

        _, cc, rtype, start, value, _, status = parts
        if status not in ("allocated", "assigned"):
            continue
        if cc == "" or cc == "ZZ":
            continue

        try:
            if rtype == "ipv4":
                prefix = 32 - (int(value).bit_length() - 1)
                net = ipaddress.ip_network(f"{start}/{prefix}", strict=False)
            elif rtype == "ipv6":
                net = ipaddress.ip_network(f"{start}/{value}", strict=False)
            else:
                continue

            countries[cc].append(str(net))
        except Exception:
            pass

# Write files
for cc, nets in countries.items():
    with open(OUT_DIR / f"{cc}.txt", "w") as f:
        for n in sorted(set(nets)):
            f.write(n + "\n")

print("Done.")
