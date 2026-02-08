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
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|")
        if len(parts) < 7:
            continue

        cc     = parts[1].strip()
        rtype  = parts[2].strip()
        start  = parts[3].strip()
        value  = parts[4].strip()
        status = parts[6].strip()

        if status not in ("allocated", "assigned"):
            continue
        if not cc or cc in ("*", "ZZ"):
            continue

        try:
            if rtype == "ipv4":
                value_int = int(value)
                if value_int <= 0:
                    continue
                prefix = 32 - (value_int.bit_length() - 1)
                net = ipaddress.ip_network(f"{start}/{prefix}", strict=False)
            elif rtype == "ipv6":
                net = ipaddress.ip_network(f"{start}/{value}", strict=False)
            else:
                continue

            countries[cc].append(str(net))
        except Exception as e:
            print(f"Skipping invalid entry from {url}: {line} → {e}")
            continue

# Write files
for cc, nets in sorted(countries.items()):
    unique_nets = sorted(set(nets), key=ipaddress.ip_network)
    cc_lower = cc.lower()
    with open(OUT_DIR / f"{cc_lower}.txt", "w") as f:
        for n in unique_nets:
            f.write(n + "\n")
    print(f"Wrote {len(unique_nets)} networks for {cc}")

print("Done.")
