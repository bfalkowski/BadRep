# ReviewLab Quick Start Guide

## 🚀 **Get Back Up and Running in 5 Minutes!**

### **1. Start the API Server**
```bash
# Navigate to project directory
cd /path/to/BadREpo

# Set GitHub token (if needed)
export GITHUB_TOKEN='your_token_here'

# Start the server
python start_api_server.py
```

**Server will be running at**: http://localhost:8000

### **2. Test the System**
```bash
# In another terminal, run the test suite
python test_api.py

# Or test individual endpoints
curl http://localhost:8000/health
```

### **3. View API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 **What's Working Right Now**

✅ **GitHub Integration** - Extract real comments from PRs  
✅ **Evaluation Engine** - Calculate precision, recall, F1-score  
✅ **REST API** - All major endpoints working  
✅ **Documentation** - Interactive API docs  

---

## 🐛 **Quick Fixes (Optional)**

### **Fix Bug Injection Endpoint**
```python
# Edit core/api_server.py line 76
bug_engine = BugInjectionEngine(project_root=".")
```

### **Fix DateTime Issue**
```python
# Edit core/github_comments.py cleanup method
# Add timezone handling for datetime comparisons
```

---

## 🚀 **Next Steps**

1. **Phase 11.3**: Cleanup System (recommended)
2. **Phase 11.5**: Learning System (advanced)
3. **Production Deployment**: Configure for production use

---

## 📚 **Full Documentation**

- **TODO.md** - Complete development status and roadmap
- **docs/PHASE_11_AGENTIC_FEATURES.md** - Detailed feature specifications
- **test_api.py** - Comprehensive API testing

---

**Status**: 🎉 **System is working and ready for development!** 🎉
