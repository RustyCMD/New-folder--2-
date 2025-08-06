# Folder Size Scanner

A modern Python GUI application that scans your entire PC to identify the 5 largest folders by total size. Features a clean dark theme interface with progress tracking and easy folder access.

## Features

- **Complete PC Scan**: Scans all available drives to find the largest folders
- **Top 5 Results**: Displays the 5 largest folders with their sizes
- **Dark Theme**: Modern dark mode interface with clean typography
- **Progress Tracking**: Real-time progress indicator during scanning
- **Easy Access**: Double-click any folder to open it in Windows Explorer
- **Human-Readable Sizes**: Displays folder sizes in KB, MB, GB, or TB format
- **Error Handling**: Gracefully handles permission errors and inaccessible directories
- **Resizable Interface**: Minimum 800x600 pixels, fully resizable

## Requirements

- **Python 3.6 or higher** (with tkinter support)
- **Windows Operating System** (optimized for Windows)
- **Administrator privileges recommended** (for accessing system folders)

## Installation

### Quick Setup

1. **Download/Clone** all files to a folder on your computer
2. **Run install.bat** - Double-click to install dependencies and verify Python setup
3. **Run start.bat** - Double-click to launch the application

### Manual Setup

If you prefer manual installation:

```bash
# Check Python installation
python --version

# Install dependencies (optional, uses built-in libraries)
pip install -r requirements.txt

# Run the application
python folder_scanner.py
```

## Usage

### Starting the Application

- **Easy Way**: Double-click `start.bat`
- **Command Line**: Run `python folder_scanner.py`

### Using the Scanner

1. **Click "Scan for Largest Folders"** to start scanning all drives
2. **Wait for completion** - The progress bar shows scanning activity
3. **View results** - The 5 largest folders will be displayed with their sizes
4. **Open folders** - Double-click any folder entry to open it in Windows Explorer
5. **Refresh** - Click "Refresh" to re-scan for updated results

### Interface Elements

- **Scan Button**: Starts the folder scanning process
- **Refresh Button**: Re-runs the scan to get updated results
- **Progress Bar**: Shows scanning activity (indeterminate progress)
- **Status Label**: Displays current scanning status and drive being processed
- **Results Table**: Shows folder path, size, and action column
- **Folder Paths**: Full paths to the largest folders found
- **Sizes**: Human-readable format (B, KB, MB, GB, TB)

## File Structure

```
folder_scanner/
├── folder_scanner.py    # Main application file
├── requirements.txt     # Python dependencies
├── install.bat         # Installation script
├── start.bat          # Launch script
└── README.md          # This file
```

## Technical Details

### How It Works

1. **Drive Detection**: Automatically detects all available drives (A: through Z:)
2. **Folder Enumeration**: Lists all top-level folders on each drive
3. **Size Calculation**: Recursively calculates total size of each folder
4. **Error Handling**: Skips inaccessible folders due to permissions
5. **Sorting**: Sorts folders by size and displays the top 5 largest
6. **Background Processing**: Uses threading to prevent GUI freezing

### Performance Notes

- **Scanning Time**: Depends on number of files and drives (typically 2-10 minutes)
- **Memory Usage**: Minimal memory footprint, processes folders one at a time
- **CPU Usage**: Low to moderate during scanning
- **Permissions**: Some system folders may be inaccessible without admin rights

### Supported Formats

- **File Systems**: NTFS, FAT32, exFAT, and other Windows-supported formats
- **Size Display**: Automatic unit conversion (B → KB → MB → GB → TB)
- **Path Handling**: Supports long Windows paths and special characters

## Troubleshooting

### Common Issues

**"Python is not installed"**
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

**"tkinter is not available"**
- Reinstall Python with tkinter support (usually included by default)
- On some Linux distributions: `sudo apt-get install python3-tk`

**"Permission denied" errors**
- Run as Administrator for access to system folders
- Some folders will always be inaccessible due to Windows security

**Application runs but shows no results**
- Check if you have any large folders on your drives
- Try running as Administrator
- Ensure drives are accessible and not encrypted

### Performance Tips

- **Close other applications** during scanning to improve performance
- **Run as Administrator** to access more folders
- **Be patient** - scanning large drives takes time
- **Use SSD drives** for faster scanning if available

## Customization

The application can be customized by modifying `folder_scanner.py`:

- **Number of results**: Change the `[:5]` in the sorting line to show more/fewer folders
- **Theme colors**: Modify the `colors` dictionary in `setup_dark_theme()`
- **Window size**: Adjust `geometry()` and `minsize()` values
- **Scan depth**: Modify the scanning logic to go deeper than top-level folders

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify Python and tkinter installation
3. Ensure all files are in the same directory
4. Try running as Administrator

---

**Version**: 1.0  
**Compatibility**: Windows 10/11, Python 3.6+  
**Last Updated**: 2025
