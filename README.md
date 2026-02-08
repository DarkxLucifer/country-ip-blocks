# Country IP Blocks Updater

Automatically fetches, parses, and updates country-level IPv4 & IPv6 address blocks (in CIDR notation) **every day** from official Regional Internet Registry (RIR) delegated statistics files.

The repository contains one `.txt` file per country code inside the `country/` folder (e.g. `in.txt`, `us.txt`, `cn.txt`, `ru.txt`, `de.txt` …), with sorted and deduplicated CIDR entries.

## Features

- Daily automatic updates via GitHub Actions (runs at 12:00 AM IST / 18:30 UTC)
- Pulls directly from primary sources: ARIN, RIPE NCC, APNIC, AFRINIC, LACNIC
- Handles both **IPv4** and **IPv6**
- One clean `.txt` file per country (lowercase ISO 3166-1 alpha-2 code)
- Only commits when data actually changes → minimal noise in history
- Robust parsing with error skipping and duplicate removal
- Manual trigger available via GitHub Actions

## Sources

Data is fetched from the latest delegated statistics files:

- ARIN:   https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest
- RIPE:   https://ftp.ripe.net/pub/stats/ripencc/delegated-ripencc-latest
- APNIC:  https://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
- AFRINIC: https://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest
- LACNIC: https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest

These files are the authoritative public records of IP address allocations and assignments.


## 📁 Folder Structure

```text
country-ip-blocks-updater/
├── .github/
│   └── workflows/
│       └── update-country-ip-blocks.yml     # GitHub Actions workflow
├── scripts/
│   └── update_country_ip.py                 # Main parsing & update script
├── country/                                 # Generated output (committed)
│   ├── in.txt
│   ├── us.txt
│   ├── cn.txt
│   └── ...
├── README.md
└── .gitignore
```




## How to Run the Code

This project is designed to run automatically via GitHub Actions every day, but you can also run it manually — either on GitHub or on your own computer.

### 1. Run Automatically (Recommended – GitHub Actions)

The workflow is already set up to run daily at **12:00 AM IST** (18:30 UTC).

To trigger it manually anytime:

1. Go to your repository on GitHub
2. Click the **Actions** tab at the top
3. On the left sidebar, select the workflow named **Update Country IP Blocks**
4. In the top-right corner, click **Run workflow** (a small ▶️ button or dropdown)
5. Click the green **Run workflow** button (you can leave the branch as `main`)

→ The script will download fresh RIR data, update the `country/` folder, and commit changes if anything is different.  
   You’ll see the progress in the workflow run logs.

### 2. Run Locally on Your Computer

You only need **Python 3.8+** and the `requests` library.

```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/DarkxLucifer/country-ip-blocks.git
cd country-ip-blocks-updater

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate          # Linux / macOS
# or on Windows: venv\Scripts\activate

# 3. Install the only required package
pip install requests

# 4. Run the script
python scripts/update_country_ip.py


