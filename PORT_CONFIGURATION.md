# 🔌 Port Configuration Summary

## Port Usage

### **Local Development**
- **Port**: `8051`
- **URL**: `http://localhost:8051`
- **Reason**: Avoids conflicts with other applications that commonly use port 8050

### **Railway Deployment**
- **Port**: `8050` (set via `PORT` environment variable)
- **URL**: `https://your-app-name.railway.app`
- **Reason**: Railway's standard port configuration

## Configuration Files

### **railway.toml**
```toml
[env]
PORT = "8050"  # Railway deployment port
```

### **app.py**
```python
# Port configuration:
# - Railway deployment: Uses PORT=8050 (set in railway.toml)
# - Local development: Uses port 8051 (to avoid conflicts with other apps)
port = int(os.getenv('PORT', 8051))
```

## Why This Setup?

1. **Local Development (8051)**:
   - Avoids conflicts with other Dash apps
   - Consistent with previous releases
   - Easy to remember

2. **Railway Deployment (8050)**:
   - Standard web application port
   - Railway's default configuration
   - Professional deployment setup

## Testing

### **Local Testing**
```bash
# Test authentication
curl -u "admin:ellingham2025" -I http://localhost:8051
# Expected: HTTP/1.1 200 OK
```

### **Railway Testing**
```bash
# Test authentication (after deployment)
curl -u "admin:ellingham_admin_2025" -I https://your-app-name.railway.app
# Expected: HTTP/1.1 200 OK
```

## Environment Variables

### **Local Development**
```bash
# No PORT needed - defaults to 8051
export ADMIN_USER=admin
export ADMIN_PASS=ellingham2025
python app.py
```

### **Railway Deployment**
```bash
# PORT=8050 set in railway.toml
# Other credentials set in Railway dashboard
```

---

**Summary**: Local development uses port 8051, Railway deployment uses port 8050. This avoids conflicts and provides a professional deployment setup.
