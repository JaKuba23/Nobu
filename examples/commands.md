# Nobu Command Examples

A collection of practical command examples for various scanning scenarios.

## Basic Scanning

### Single Host - Common Ports
```bash
nobu scan --target 192.168.1.1 --ports 1-1024
```

### Single Host - Specific Ports
```bash
nobu scan --target 192.168.1.1 --ports 22,80,443,3306,8080
```

### Hostname Resolution
```bash
nobu scan --target example.com --ports 80,443
```

---

## Profile-Based Scanning

### Fast Reconnaissance
```bash
nobu profile fast --target 192.168.1.1
```

### Web Server Discovery
```bash
nobu profile web --target webserver.local
```

### Database Detection
```bash
nobu profile database --target db.internal
```

### Email Server Check
```bash
nobu profile mail --target mail.example.com
```

### Full Port Scan (1-1024)
```bash
nobu profile full --target 10.0.0.5
```

### Low-Profile Stealth Scan
```bash
nobu profile stealth --target sensitive-host.local
```

---

## Network Scanning

### Subnet /24 Scan
```bash
nobu scan --target 192.168.1.0/24 --ports 22,80,443
```

### Smaller Subnet /28
```bash
nobu scan --target 10.0.0.0/28 --ports 80,443,8080
```

### Home Network Discovery
```bash
nobu scan --target 192.168.0.0/24 --ports 22,80,443,445,3389 --threads 200
```

---

## Banner Grabbing

### HTTP Banner Detection
```bash
nobu scan --target 192.168.1.1 --ports 80,8080,8443 --banner
```

### Service Identification
```bash
nobu profile fast --target example.com --banner
```

---

## Output Options

### Export to JSON
```bash
nobu scan --target 192.168.1.1 --ports 1-1024 --output results.json
```

### Export to CSV
```bash
nobu profile fast --target 10.0.0.1 --output scan_results.csv
```

### Quiet Mode (Open Ports Only)
```bash
nobu scan --target 192.168.1.0/24 --ports 22,80,443 --quiet
```

### No Colors (For Piping/Logging)
```bash
nobu scan --target 192.168.1.1 --ports 1-1024 --no-color > scan.log
```

### Verbose Debug Output
```bash
nobu scan --target localhost --ports 80 --verbose
```

---

## Performance Tuning

### High Thread Count (Fast Networks)
```bash
nobu scan --target 192.168.1.0/24 --ports 1-1024 --threads 500
```

### Low Thread Count (Stealth)
```bash
nobu scan --target target.local --ports 1-1024 --threads 10
```

### Extended Timeout (Slow Hosts)
```bash
nobu scan --target slow-host.example.com --ports 80,443 --timeout 5.0
```

### Fast Timeout (Quick Scan)
```bash
nobu scan --target 192.168.1.1 --ports 1-1024 --timeout 0.3 --threads 200
```

---

## Common Use Cases

### Check if SSH is Open
```bash
nobu scan --target server.local --ports 22
```

### Find Web Servers on Network
```bash
nobu scan --target 192.168.1.0/24 --ports 80,443,8080,8443 --quiet
```

### Database Server Discovery
```bash
nobu scan --target 10.0.0.0/24 --ports 3306,5432,27017,6379,1433
```

### Check Common Remote Access Ports
```bash
nobu scan --target 192.168.1.0/24 --ports 22,23,3389,5900
```

### Verify Firewall Rules
```bash
nobu scan --target firewall.local --ports 1-1024 --timeout 2.0
```

---

## Combination Examples

### Full Recon with Banner and Export
```bash
nobu profile fast --target 192.168.1.1 --banner --output recon.json
```

### Quiet Network Scan to CSV
```bash
nobu scan --target 10.0.0.0/24 --ports 22,80,443 --quiet --no-color --output network.csv
```

### Verbose Debug Scan
```bash
nobu scan --target localhost --ports 1-100 --verbose --banner
```

---

## Tips

1. **Start with profiles** for quick reconnaissance
2. **Use `--quiet`** when scanning large networks
3. **Increase threads** for faster scans on reliable networks
4. **Lower threads** and increase timeout for stealth
5. **Always export results** for documentation
6. **Use CIDR carefully** - large ranges take time

---

## Getting Help

```bash
# Main help
nobu --help

# Scan command help
nobu scan --help

# Profile command help
nobu profile --help

# Version info
nobu --version
```

