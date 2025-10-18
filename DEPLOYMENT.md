# 🚀 Railway Deployment Guide

## Off-Equilibrium Ellingham Diagram - Private Access

This guide will help you deploy your authenticated Ellingham Diagram app to Railway with private access control.

## 🔐 Authentication Setup

The app now includes three access levels:

### **Admin Access** (Full Control)
- **Username**: `ricfulop` (or set via `ADMIN_USER` env var)
- **Password**: `ellingham_admin_2025` (or set via `ADMIN_PASS` env var)
- **Access**: Full app functionality

### **Researcher Access** (Research Use)
- **Username**: `researcher` (or set via `RESEARCHER_USER` env var)
- **Password**: `research_access_2025` (or set via `RESEARCHER_PASS` env var)
- **Access**: Full app functionality

### **Student Access** (Educational Use)
- **Username**: `student` (or set via `STUDENT_USER` env var)
- **Password**: `student_access_2025` (or set via `STUDENT_PASS` env var)
- **Access**: Full app functionality

## 🚀 Deployment Steps

### **1. Install Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### **2. Deploy to Railway**
```bash
# Initialize Railway project
railway init

# Deploy the app
railway up
```

### **3. Set Environment Variables**
In Railway dashboard, set these environment variables:

```bash
# Authentication
ADMIN_USER=ricfulop
ADMIN_PASS=your_secure_admin_password
RESEARCHER_USER=researcher
RESEARCHER_PASS=your_secure_researcher_password
STUDENT_USER=student
STUDENT_PASS=your_secure_student_password

# Deployment
PORT=8050
DEBUG=False
```

### **4. Custom Domain (Optional)**
- Go to Railway dashboard
- Select your project
- Go to Settings → Domains
- Add your custom domain (e.g., `ellingham.mit.edu`)

## 🔧 Local Development

### **Run with Authentication Locally**
```bash
# Set environment variables
export ADMIN_USER=admin
export ADMIN_PASS=local_password
export RESEARCHER_USER=researcher
export RESEARCHER_PASS=local_research_password
export STUDENT_USER=student
export STUDENT_PASS=local_student_password

# Run the app
python app.py
```

### **Access Locally**
- **URL**: `http://localhost:8051` (local development port)
- **Login**: Use any of the three username/password combinations

## 🛡️ Security Features

### **Environment-Based Credentials**
- Passwords stored as environment variables (not in code)
- Different credentials for different access levels
- Easy to change passwords without code changes

### **HTTPS by Default**
- Railway provides automatic HTTPS
- Secure authentication over encrypted connection

### **Access Control**
- Basic HTTP authentication
- Simple username/password protection
- No complex user registration needed

## 📊 Usage Instructions

### **For Administrators**
1. Use admin credentials to access full functionality
2. Share researcher/student credentials as needed
3. Monitor usage through Railway dashboard

### **For Researchers**
1. Use researcher credentials for research work
2. Full access to all thermodynamic calculations
3. Can export data and generate reports

### **For Students**
1. Use student credentials for educational purposes
2. Full access to learning features
3. Can explore different materials and conditions

## 🔄 Updates and Maintenance

### **Deploy Updates**
```bash
# Push changes to GitHub
git add .
git commit -m "Update app features"
git push origin main

# Railway auto-deploys from GitHub
```

### **Change Passwords**
1. Update environment variables in Railway dashboard
2. Redeploy the app
3. Share new credentials with users

### **Monitor Usage**
- Check Railway dashboard for usage statistics
- Monitor app performance and errors
- View logs for troubleshooting

## 🎯 Benefits

### **Private Access**
- ✅ Controlled access with username/password
- ✅ No public access to your research app
- ✅ Easy to share credentials with collaborators

### **Professional Setup**
- ✅ Custom domain support
- ✅ Automatic HTTPS
- ✅ Professional URL (e.g., `ellingham-diagram.railway.app`)

### **Easy Management**
- ✅ Environment-based configuration
- ✅ Easy password changes
- ✅ Automatic deployments from GitHub

## 🆘 Troubleshooting

### **Authentication Issues**
- Check environment variables are set correctly
- Verify username/password combinations
- Check Railway logs for errors

### **Deployment Issues**
- Ensure all dependencies are in `requirements.txt`
- Check `railway.toml` configuration
- Verify GitHub repository connection

### **Performance Issues**
- Monitor Railway dashboard for resource usage
- Check app logs for errors
- Consider upgrading Railway plan if needed

---

**Ready to deploy?** Follow the steps above to get your private Ellingham Diagram app online! 🚀
