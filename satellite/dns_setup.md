# Spacecraft Thermal OS (AST-OS) - SaaS Domain & DNS Configuration

This document specifies the DNS record setups, subdomain routing mappings, and SSL certificates configurations required to host AST-OS production services under the official `ast-os.com` domain.

---

## 1. Domain DNS Record Specifications

Configure the DNS zones inside your registrar (Cloudflare, GoDaddy, Namecheap) conforming to the following zone table:

| Subdomain Host | Record Type | Target IP / Canonical Name | TTL | Routing Purpose |
| --- | :---: | --- | :---: | --- |
| **`api.ast-os.com`** | **A Record** | `49.12.104.22` (Target Hetzner VPS IP) | 300s | Exposes the FastAPI SaaS backend endpoints. |
| **`docs.ast-os.com`** | **CNAME** | `ast-os.github.io` (GitHub Pages page) | 3600s | Hosts the static Docusaurus/MkDocs developer references. |
| **`dashboard.ast-os.com`**| **CNAME** | `ast-os-dashboard.vercel.app` | 300s | Exposes the Next.js visual dashboard UI interface. |
| **`ast-os.com`** | **A Record** | `49.12.104.22` (VPS IP) | 300s | Apex domain routing to product landing showcase. |

---

## 2. Cloudflare Proxying & SSL Settings

To protect the server from DDoS attacks and leverage automated edge SSL certificates:
1. **SSL/TLS Encryption Mode**: Set to **Full (Strict)**. This ensures data is fully encrypted from Cloudflare’s edge to Nginx reverse-proxies.
2. **DNS Proxy Status**: Enable Cloudflare Proxying (orange cloud active) for `api` and apex domains to mask real VPS backend server IPs.
3. **Always Use HTTPS**: Enable the redirect rule to upgrade HTTP requests to secure HTTPS.
