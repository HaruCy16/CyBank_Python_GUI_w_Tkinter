# CyBank - Setup & Troubleshooting Guide

## ✅ Fixed: Import Resolution Issues

The project now includes proper configuration files to ensure imports work correctly on **any computer** without manual setup.

---

## 🔧 What Was Fixed

### **Files Added:**

1. **`.vscode/settings.json`** - VS Code Python configuration
   - Automatically sets Python path to workspace folder
   - Configures Pylance to recognize project structure
   - Sets PYTHONPATH for integrated terminals

2. **`run.py`** - Application launcher script
   - Sets up Python path before importing modules
   - Ensures consistent behavior across all computers

3. **`.env`** - Environment configuration
   - Defines PYTHONPATH for the project

### **How It Works:**

When you open the project in VS Code:
1. VS Code reads `.vscode/settings.json`
2. Python analysis path is set to workspace folder
3. All imports resolve correctly
4. No manual configuration needed!

---

## 🚀 Running the Application

### **Method 1: Using the Launcher (EASIEST)**
```bash
python run.py
```
✅ **Recommended** - Works on any computer, any configuration

### **Method 2: As a Python Module**
```bash
python -m cli.main
```
✅ Works without any setup

### **Method 3: Direct Execution**
```bash
python cli/main.py
```
✅ Works because `main.py` has built-in path setup

---

## 🖥️ Setting Up on a New Computer

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/HaruCy16/CyBank_Python_GUI_w_Tkinter.git
cd CyBank
```

### **Step 2: Open in VS Code**
```bash
code .
```

### **Step 3: Verify Python Version**
```bash
python --version
```
Ensure Python 3.8 or higher is installed.

### **Step 4: Run the Application**
```bash
python run.py
```

That's it! No additional configuration needed.

---

## 🐛 Troubleshooting

### **Issue: Import errors in VS Code**

**Symptoms:**
- Yellow warning triangles in Error List
- "Import could not be resolved" messages
- Code runs fine but shows errors in IDE

**Solution:**
1. **Reload VS Code window:**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type "Reload Window"
   - Press Enter

2. **Verify `.vscode/settings.json` exists:**
   ```bash
   dir .vscode\settings.json
   ```
   If missing, the file should contain:
   ```json
   {
       "python.analysis.extraPaths": [
           "${workspaceFolder}"
       ],
       "terminal.integrated.env.windows": {
           "PYTHONPATH": "${workspaceFolder}"
       }
   }
   ```

3. **Check Python interpreter:**
   - Click on Python version in bottom-left of VS Code
   - Select the correct Python interpreter
   - Restart VS Code

---

### **Issue: Module not found when running**

**Symptoms:**
```
ModuleNotFoundError: No module named 'backend'
```

**Solution:**
Run using the launcher or module syntax:
```bash
python run.py
```
OR
```bash
python -m cli.main
```

**Do NOT run:**
```bash
cd cli
python main.py  # ❌ This breaks imports
```

---

### **Issue: Application won't start**

**Symptoms:**
- Python command not recognized
- Syntax errors
- Import errors even with launcher

**Solution:**

1. **Verify Python installation:**
   ```bash
   python --version
   ```
   Should show Python 3.8 or higher.

2. **Check if you're in the correct directory:**
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   ```
   Should show: `.../CyBank`

3. **Verify all files exist:**
   ```bash
   dir run.py          # Windows
   ls run.py           # Linux/Mac
   ```

4. **Try alternative Python command:**
   ```bash
   python3 run.py      # If 'python' doesn't work
   py run.py           # Windows Python Launcher
   ```

---

### **Issue: Password input not showing asterisks**

**Symptoms:**
- Password field is completely blank when typing
- No visual feedback

**This is normal behavior on some systems:**
- Windows with `msvcrt` module: Shows asterisks (*)
- Linux/Mac or systems without `msvcrt`: Hides input completely (no asterisks)

Both are secure! The password is still being captured, just not displayed.

---

### **Issue: Colors not showing in terminal**

**Symptoms:**
- Terminal shows ANSI codes like `\033[38;2;139;69;19m`
- Colors appear as text instead of colored output

**Solution:**

**Windows (PowerShell):**
```powershell
$host.UI.SupportsVirtualTerminal = $true
```
Then run the application.

**Windows (Command Prompt):**
Use Windows Terminal instead:
```bash
wt python run.py
```

**Linux/Mac:**
Should work by default. If not, update terminal emulator.

---

## 📋 System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows, Linux, or macOS
- **Terminal:** Any terminal with Python support
- **Dependencies:** None (uses Python standard library only)

---

## 🎯 Best Practices for Team Development

### **When Sharing Code:**
1. ✅ Always commit `.vscode/settings.json`
2. ✅ Always commit `run.py`
3. ✅ Always commit `.env`
4. ✅ Include this SETUP_GUIDE.md in documentation
5. ✅ Tell team members to use `python run.py`

### **When Pulling Changes:**
1. Open project in VS Code
2. Reload window (`Ctrl+Shift+P` → "Reload Window")
3. Run `python run.py`

### **When Adding New Modules:**
1. Create `__init__.py` in new package folders
2. Use absolute imports (`from backend.services...`)
3. Test with `python run.py`

---

## ✅ Verification Checklist

Run these commands to verify setup:

```bash
# 1. Check Python version
python --version

# 2. Check if in correct directory
pwd  # Should show: .../CyBank

# 3. Verify files exist
dir run.py
dir .vscode\settings.json

# 4. Test imports (should show no errors)
python -c "from backend.services.user_service import register_user; print('✅ Imports work!')"

# 5. Run application
python run.py
```

If all 5 steps work, setup is complete! ✅

---

## 🎉 Summary

The project is now configured to work on **any computer** without manual setup:

✅ **VS Code configuration** - Automatic Python path setup  
✅ **Launcher script** - Consistent execution across systems  
✅ **Environment file** - PYTHONPATH configuration  
✅ **Documentation** - Clear instructions for team  

**Just run:** `python run.py` and you're ready to go! 🚀

---

*Last Updated: Phase 4 Completion - December 2025*
