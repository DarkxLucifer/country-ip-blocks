# 🌍 Country IP Blocks

A curated collection of **IPv4 and IPv6 CIDR blocks grouped by country**.
This repository helps developers, network administrators, and security engineers easily implement **country-based IP filtering and geo-restriction rules**.

The IP ranges are derived from official **Regional Internet Registry (RIR)** allocation data and organized in a simple format for quick integration into firewalls, servers, and security tools.

---

## 📦 Features

* 🌎 Country-based IP block lists
* 🔢 IPv4 and IPv6 CIDR ranges
* ⚡ Easy integration with firewalls and servers
* 🛡 Useful for geo-blocking and security filtering
* 📁 Organized and easy-to-use file structure
* 🔄 Designed for periodic updates

---

## 📂 Repository Structure

```
country-ip-blocks/
│
├── ipv4/
│   ├── us.txt
│   ├── in.txt
│   ├── cn.txt
│   └── ...
│
├── ipv6/
│   ├── us.txt
│   ├── in.txt
│   ├── cn.txt
│   └── ...
│
└── README.md
```

Each file contains **CIDR IP ranges belonging to a specific country**.

Example:

```
1.0.0.0/24
1.0.4.0/22
1.0.16.0/20
```

---

## 🚀 Use Cases

This repository can be used for:

* 🔐 Firewall country blocking
* 🌍 Geo-restricted services
* 🛡 Security and abuse prevention
* 📊 Network analysis
* 🖥 Server access control
* 🚫 Blocking malicious traffic from specific regions

---

## ⚙️ Example Usage

### Example: Block a Country in Nginx

```
deny 1.0.0.0/24;
deny 1.0.4.0/22;
```

### Example: Linux Firewall (iptables)

```
iptables -A INPUT -s 1.0.0.0/24 -j DROP
```

---

## 📊 Data Sources

IP ranges originate from the official **Regional Internet Registries**:

* ARIN
* RIPE NCC
* APNIC
* LACNIC
* AFRINIC

These organizations manage global IP address allocations.

---

## ⚠️ Disclaimer

* IP geolocation is **not always 100% accurate**.
* Some IP addresses may be used outside their registered country.
* Always test rules before applying them in production.

---

## 🤝 Contributing

Contributions are welcome!

If you want to:

* Improve data accuracy
* Add scripts for automated updates
* Improve documentation

Feel free to open a **Pull Request** or **Issue**.

---

## ⭐ Support

If you find this project useful, consider **starring the repository** ⭐

---

## 📜 License

This project is released under the **MIT License**.
