# Nobu Test Lab 🧪

A Docker-based test environment for safely testing the Nobu port scanner.

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check running containers
docker-compose ps

# Scan the lab
nobu scan --target 127.0.0.1 --ports 21,1025,2222,3306,5432,6379,8025,8080,8081,27017 --banner

# Or use the lab profile (after creating it)
nobu profile lab --target 127.0.0.1
```

## Available Services

| Service     | Port(s)     | Description                  |
|-------------|-------------|------------------------------|
| Nginx       | 8080, 8443  | Web server (HTTP/HTTPS)      |
| Apache      | 8081        | Alternative web server       |
| SSH         | 2222        | OpenSSH server               |
| MySQL       | 3306        | MySQL 8.0 database           |
| PostgreSQL  | 5432        | PostgreSQL 15 database       |
| Redis       | 6379        | Redis cache                  |
| MongoDB     | 27017       | MongoDB 6 database           |
| MailHog     | 1025, 8025  | SMTP test server + Web UI    |
| FTP         | 21          | vsftpd FTP server            |

## Test Credentials

All services use test credentials - **DO NOT use in production!**

- **SSH:** `scanner` / `nobutest`
- **MySQL:** `root` / `nobutest`
- **PostgreSQL:** `postgres` / `nobutest`
- **MongoDB:** `admin` / `nobutest`
- **FTP:** `scanner` / `nobutest`

## Example Scans

### Full Lab Scan
```bash
nobu scan --target 127.0.0.1 \
  --ports 21,1025,2222,3306,5432,6379,8025,8080,8081,27017 \
  --banner --timeout 2
```

### Web Servers Only
```bash
nobu scan --target 127.0.0.1 --ports 8080,8081,8443 --banner
```

### Databases Only
```bash
nobu scan --target 127.0.0.1 --ports 3306,5432,6379,27017 --banner
```

### Export Results
```bash
nobu scan --target 127.0.0.1 \
  --ports 21,1025,2222,3306,5432,6379,8025,8080,8081,27017 \
  --output lab-results.json
```

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (delete data)
docker-compose down -v

# Remove everything including images
docker-compose down --rmi all -v
```

## Network Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      nobu-test-network                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │  Nginx  │  │ Apache  │  │   SSH   │  │   FTP   │              │
│  │  :8080  │  │  :8081  │  │  :2222  │  │   :21   │              │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │  MySQL  │  │PostgreSQL│ │  Redis  │  │ MongoDB │              │
│  │  :3306  │  │  :5432  │  │  :6379  │  │ :27017  │              │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
│                                                                   │
│  ┌─────────────────┐                                             │
│  │    MailHog      │                                             │
│  │ :1025 (SMTP)    │                                             │
│  │ :8025 (Web UI)  │                                             │
│  └─────────────────┘                                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Nobu Scanner  │
                    │   127.0.0.1     │
                    └─────────────────┘
```

## Why Use This Lab?

1. **Safe** - All traffic stays on localhost
2. **Legal** - You own these services
3. **Realistic** - Real services with real banners
4. **Reproducible** - Same results every time
5. **Educational** - Learn about different services

---

Happy scanning! 🔍

