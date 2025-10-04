# UC Learn Class List Generator

## Project Overview

This project provides a self-contained tool for extracting participant lists from UC Learn courses. The tool is designed to work on any Windows machine without requiring Python installation or administrative privileges.

## Project Structure

### End-User Distribution
- **`generate_classlist.zip`** - Complete self-contained package for end users
- **`GENERATE_CLASSLIST.bat`** - Main launcher script
- **`README.txt`** - End-user instructions

### Core Components
- **`scraper_python3_self_contained.py`** - Main scraper with auto-setup
- **`portable_scraper.py`** - Browser automation and driver management
- **`manual_scraper.py`** - Base scraper functionality
- **`uc_learn_scraper.py`** - Core UC Learn interaction logic

### Browser Drivers
- **`chromedriver.exe`** - Chrome browser driver
- **`geckodriver.exe`** - Firefox browser driver

### Dependencies
- **`requirements.txt`** - Python package requirements

## Technical Features

### Self-Contained Operation
- Downloads portable Python 3.11 automatically (first run only)
- Installs required packages to portable environment
- No system modifications or admin rights required

### Browser Compatibility
- Supports Chrome and Firefox
- Automatic driver version detection and updates
- Fallback mechanisms for driver compatibility

### Robust Operation
- Multiple fallback strategies for browser setup
- Comprehensive error handling and troubleshooting
- Automatic dependency management

## Usage

### For End Users
1. Extract `generate_classlist.zip`
2. Run `GENERATE_CLASSLIST.bat`
3. Follow prompts for course name and login

### For Developers
- All source files are included for modification
- Standard Python packaging with requirements.txt
- Modular design for easy customization

## Distribution

The `generate_classlist.zip` file contains everything needed for end-user deployment:
- Self-contained Python environment setup
- Browser drivers with auto-update capability
- Complete documentation and troubleshooting

## Requirements

### System Requirements
- Windows 7/8/10/11
- Internet connection (first run only)
- Chrome or Firefox browser

### No Installation Required
- Python: Downloaded automatically
- Packages: Installed automatically
- Drivers: Bundled with auto-update fallback

## Version History

**Self-Contained Distribution**
- Portable Python 3.11 integration
- Automatic driver management
- Zero-dependency operation
- Complete Windows compatibility

---

**Maintained by**: UC Learn Automation Project  
**Compatible**: Windows 7/8/10/11  
**Last Updated**: October 2025