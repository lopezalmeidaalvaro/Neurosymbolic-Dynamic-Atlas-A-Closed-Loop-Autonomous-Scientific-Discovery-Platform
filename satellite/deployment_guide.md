# Spacecraft Thermal OS (AST-OS) - Production SaaS Deployment Guide

This guide details the systems engineering procedures required to package, deploy, and scale the AST-OS SaaS FastAPI applications inside dedicated VPS cloud providers (Hetzner, AWS, digitalOcean).

---

## 1. Local Package Packaging

### A. Environment Preparation
Copy the environment template and configure secrets:
```bash
cp .env.example .env
nano .env
```
Ensure that `JWT_SECRET` is changed to a high-entropy string and that `STRIPE_SECRET_KEY` matches Stripe's dashboard settings.

### B. Building Docker Images
Build the multi-stage production runner:
```bash
docker compose build --no-cache
```

---

## 2. Multi-Service Composition

Launch all services (TimescaleDB, Redis, and FastAPI) in detached daemon mode:
```bash
docker compose up -d
```

Verify service execution logs:
```bash
docker compose ps
docker compose logs -f fastapi
```

---

## 3. Production Hardening & Security

### A. Nginx Reverse-Proxy Configurations
Install Nginx on the target host as the frontend reverse-proxy:
```bash
sudo apt-get update
sudo apt-get install -y nginx
```

Write the server block `/etc/nginx/sites-available/ast-os`:
```nginx
server {
    listen 80;
    server_name api.ast-os.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the configuration and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/ast-os /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### B. SSL Encryption via Let's Encrypt Certbot
To secure routes under HTTPS (`https://api.ast-os.com`):
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.ast-os.com
```

---

## 4. Systems Telemetry & Scaling

* **Prometheus Targets**: Configure `/v1/metrics` endpoints inside `/etc/prometheus/prometheus.yml` to dynamically track query speeds and load averages.
* **Auto-Restart watchdogs**: Systemd or Docker restarts policies (`restart: always`) are deployed to recover services from severe exceptions or kernel reboots.
