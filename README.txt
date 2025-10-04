# UC Learn Class List Generator

## Quick Start Guide

### What This Does
This tool automatically extracts participant lists from UC Learn courses without requiring any Python installation or technical setup.

### Requirements
- Windows computer
- Internet connection (for first-time setup only)
- Access to UC Learn course

### How to Use

1. **Extract** this ZIP file to any folder on your computer
2. **Double-click** `GENERATE_CLASSLIST.bat`
3. **First run**: The tool will automatically download Python (~30MB) - this only happens once
4. **Enter** your course name when prompted (e.g., MBAM604)
5. **Browser opens**: Complete the UC Learn login when prompted
6. **Results**: Course participant list saved as `participants.json`

### What Happens on First Run
- Downloads portable Python 3.11 (about 30MB)
- Installs required packages automatically
- Sets up browser drivers
- All files stay in this folder - no system changes

### What Happens on Subsequent Runs
- Uses cached Python environment (instant startup)
- Opens browser for UC Learn login
- Extracts participant data

### Output
- `participants.json` - Course participant list in JSON format
- Can be opened with Notepad or Excel

### Troubleshooting
- **Download fails**: Check internet connection
- **Browser won't open**: Ensure Chrome or Firefox is installed
- **Login fails**: Verify UC Learn credentials and course access
- **No results**: Check course name spelling

### Technical Notes
- No admin rights required
- No Python installation needed
- All files contained in this folder
- Automatic browser driver updates
- Works offline after initial setup

### Support
This is a self-contained tool. All required files are included.

---
**Version**: Self-Contained Distribution  
**Compatible**: Windows 7/8/10/11  
**Browser Support**: Chrome, Firefox (automatic detection)