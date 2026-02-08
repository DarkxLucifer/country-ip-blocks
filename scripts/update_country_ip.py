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
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.text
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        continue

    for line in data.splitlines():
        if line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < 7:
            continue

        _, cc, rtype, start, value, _, status = parts[:7]  # Take only first 7 to avoid unpack errors
        if status not in ("allocated", "assigned"):
            continue
        if cc == "" or cc == "ZZ":
            continue

        try:
            if rtype == "ipv4":
                value_int = int(value)
                if value_int == 0:
                    continue
                prefix = 32 - (value_int.bit_length() - 1)
                net = ipaddress.ip_network(f"{start}/{prefix}", strict=False)
            elif rtype == "ipv6":
                net = ipaddress.ip_network(f"{start}/{value}", strict=False)
            else:
                continue

            countries[cc].append(str(net))
        except Exception as e:
            print(f"Error processing line '{line}': {e}")
            pass

# Write files
for cc, nets in sorted(countries.items()):
    unique_nets = sorted(set(nets), key=lambda x: (ipaddress.ip_network(x).version, ipaddress.ip_network(x)))
    with open(OUT_DIR / f"{cc.lower()}.txt", "w") as f:
        for n in unique_nets:
            f.write(n + "\n")

print("Done.")
