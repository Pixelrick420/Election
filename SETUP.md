# Election Management System - Setup Guide

A comprehensive election management system built with Python and Tkinter for Ubuntu/Linux systems.

## Prerequisites

- Python 3.8 or higher
- Ubuntu/Linux system (tested on Ubuntu)
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Pixelrick420/Election.git
cd Election
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt indicating the virtual environment is active.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Directory Structure

Your project should look like this:
```
Election/
├── election_app/
│   ├── __init__.py
│   ├── db.py
│   ├── dialogs.py
│   ├── exporter.py
│   ├── security.py
│   ├── ui.py
│   └── voting.py
├── symbols/
│   ├── auto.png
│   ├── book.png
│   ├── bottle.png
│   ├── eraser.png
│   ├── fan.png
│   ├── lightbulb.png
│   ├── pencil.png
│   ├── tree.png
│   └── umbrella.png
├── results/          (will be created automatically)
├── venv/            (your virtual environment)
├── run.py
├── requirements.txt
├── .gitignore
└── SETUP.md
```

## Running the Application

### 1. Make Sure Virtual Environment is Active

```bash
source venv/bin/activate
```

### 2. Run the Application

```bash
python3 run.py
```

The Election Management System GUI will launch.

## First Time Usage

1. **Create an Election**: Click the "Add" button in the Elections panel
2. **Set Admin Password**: Choose a secure password for election administration
3. **Add Candidates**: Select your election and use "Add Candidate" to add participants
4. **Upload Symbols**: Each candidate can have a symbol image from the `symbols/` directory
5. **Start Voting**: Click "Start Voting" to begin the election process

## Features

- **Election Management**: Create, edit, and delete elections
- **Candidate Management**: Add candidates with names and symbol images
- **Secure Voting**: Password-protected admin functions
- **Real-time Results**: View live voting results
- **Export Functionality**: Export results to JSON, CSV, and PDF formats
- **NOTA Support**: "None of the Above" option automatically included

## Troubleshooting

### Virtual Environment Issues

If you see import errors, make sure your virtual environment is activated:
```bash
source venv/bin/activate
pip list  # Should show bcrypt and Pillow
```

### Missing Dependencies

If you get import errors, reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Permission Issues

Make sure the results directory is writable:
```bash
chmod 755 results/
```

### Symbol Images Not Loading

Ensure symbol files are in the `symbols/` directory and are valid PNG files.

## Development

### Adding New Symbols

Place PNG image files in the `symbols/` directory. Recommended size: 64x64 pixels.

### Database Location

The SQLite database `elections.db` is created automatically in the project root.

### Customizing the UI

The main UI components are in `election_app/ui.py`. Font sizes and styling can be adjusted there.

## System Requirements

- **RAM**: Minimum 512MB (1GB recommended)
- **Storage**: 100MB free space
- **Display**: 1440x780 minimum resolution (for larger fonts)
- **Python Libraries**: Listed in requirements.txt

## Security Features
- Password hashing using bcrypt
- Admin password protection for sensitive operations
- Secure election data management
- Vote integrity protection

## Support

For issues and questions:
1. Check this setup guide
2. Review the error messages carefully
3. Ensure all dependencies are installed
4. Verify file permissions


**Note**: This application is designed for educational and small-scale election purposes. For large-scale or official elections, additional security measures and testing would be required.
