# Election Management System

A comprehensive Python-based election management application designed for school and classroom elections. This system provides a secure, user-friendly interface for managing elections, candidates, and voting processes on a single machine.

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Guide](#usage-guide)
- [Database Schema](#database-schema)
- [Security Features](#security-features)
- [Export Formats](#export-formats)
- [Configuration](#configuration)
- [Screenshots](#screenshots)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Functionality
- **Multi-Election Support**: Create and manage multiple elections with independent candidate pools
- **Candidate Management**: Add, edit, and delete candidates with optional symbol images
- **Secure Voting Interface**: Full-screen kiosk mode preventing access to other applications
- **Real-time Results**: View live vote counts and percentage calculations
- **NOTA Support**: Automatic "None of the Above" option for democratic compliance
- **Password Protection**: SHA-256 hashed admin authentication for election management

### Export & Reporting
- **Multiple Export Formats**: JSON, CSV, and PDF reports with comprehensive data
- **Automatic Timestamping**: All exports include generation timestamps for audit trails
- **Symbol Integration**: Candidate symbols embedded in PDF reports
- **Fallback Support**: Text reports generated when PDF dependencies unavailable

### User Experience
- **Intuitive GUI**: Clean, modern interface with optimized spacing and typography
- **Audio Feedback**: System beep sounds for vote confirmation and administrative actions
- **Responsive Design**: Adaptive layout supporting various screen resolutions
- **Accessibility**: High contrast colors and large fonts optimized for voting scenarios

## System Requirements

### Operating System
- **Primary**: Ubuntu 22.04 LTS (fully optimized and tested)
- **Compatible**: Any Linux distribution with X11 display server
- **Limited Support**: Windows, macOS (some audio and system integration features unavailable)

### Python Requirements
- **Python**: 3.8 or higher (3.10+ recommended)
- **Core Libraries**: Tkinter (GUI), SQLite3 (database), Pillow (image processing)
- **Optional Libraries**: ReportLab (PDF generation), PulseAudio utilities (enhanced audio)

### Hardware
- **Minimum RAM**: 2GB available memory
- **Storage**: 100MB free disk space for application and database
- **Display**: 1024x768 minimum resolution (1920x1080 recommended)
- **Audio**: Optional sound card for voting feedback audio

## Installation

### Method 1: Automated Setup (Recommended for Non-Technical Users)

The automated setup script handles all dependencies, environment configuration, and installation steps.

```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/Pixelrick420/Election/main/setup.sh
chmod +x setup.sh
./setup.sh
```

The setup script performs the following operations:
- System compatibility verification (Ubuntu 22.04 optimization)
- Package repository updates
- Git, Python3, and development tools installation
- Repository cloning from GitHub
- Virtual environment creation and activation
- Python dependency installation and compilation
- Directory structure creation
- Optional desktop shortcut generation
- Application launch verification

### Method 2: Manual Installation (Advanced Users)

#### 1. Clone Repository
```bash
git clone https://github.com/Pixelrick420/Election.git
cd Election
```

#### 2. System Dependencies (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk python3-dev build-essential
```

#### 3. Python Environment Setup
```bash
# Create isolated virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade package installer
pip install --upgrade pip
```

#### 4. Install Python Dependencies
```bash
# Core requirements
pip install Pillow>=9.0.0

# Optional: PDF generation capability
pip install reportlab>=3.6.0

# Optional: Enhanced image processing
pip install Pillow[imagingft]
```

#### 5. Directory Structure Creation
```bash
mkdir -p symbols results
chmod 755 symbols results
```

## Quick Start

### 1. Application Launch
```bash
# If using automated setup
cd Election
source venv/bin/activate
python3 run.py

# Alternative: Use desktop shortcut (if created during setup)
```

### 2. Election Creation Workflow
1. Launch application and observe Elections panel on left side
2. Click **Add** button to create new election
3. Enter descriptive election name (e.g., "Student Council President 2025")
4. Configure strong admin password (minimum 8 characters recommended)
5. Confirm creation and observe election appears in list

### 3. Candidate Registration Process
1. Select election from list (authentication required)
2. Enter admin password when prompted
3. Navigate to Candidates section in right panel
4. Click **Add Candidate** button
5. Enter candidate full name
6. Browse for symbol image (optional but recommended)
7. Confirm addition and repeat for all candidates

### 4. Voting Session Management
1. Verify all candidates added correctly
2. Click **Start** button to enter voting mode
3. System transitions to full-screen kiosk interface
4. Voters interact with candidate selection buttons
5. Vote casting requires Enter key confirmation
6. Next ballot accessed via Space key

### 5. Results Analysis and Export
1. End voting session using Ctrl+Q key combination
2. Provide admin password authentication
3. System automatically exports results in all formats
4. Access **View** button for real-time results display
5. Use **Export** button for manual export to custom directory

## Architecture

### Module Structure
```
election_app/
├── __init__.py           # Package initialization and version info
├── db.py                 # SQLite database management with connection pooling
├── main.py               # Primary UI components and application logic
├── voting.py             # Full-screen voting interface with security features
├── dialogs.py            # Modal dialog components (Election, Candidate)
├── security.py           # Cryptographic functions and password management
└── exporter.py           # Multi-format results export functionality
```

### Component Architecture

#### DatabaseManager (db.py)
- **Purpose**: Thread-safe SQLite database operations with connection management
- **Features**: Automatic schema migration, foreign key constraint enforcement, connection pooling
- **Threading**: Implements locking mechanism for concurrent access safety

#### ElectionApp (main.py)
- **Purpose**: Main application window providing election and candidate management
- **Framework**: Tkinter with enhanced styling and responsive layout design
- **Features**: CRUD operations, password authentication, results visualization

#### VotingInterface (voting.py)
- **Purpose**: Secure full-screen voting experience with kiosk mode functionality
- **Security**: System key disabling, admin password exit requirement, process isolation
- **Accessibility**: Large buttons, audio feedback, keyboard navigation support

#### ResultsExporter (exporter.py)
- **Purpose**: Multi-format report generation with error handling and fallback mechanisms
- **Formats**: JSON (structured data), CSV (spreadsheet compatibility), PDF (professional reports)
- **Features**: Automatic timestamping, symbol embedding, graceful degradation

## Usage Guide

### Election Management Operations

#### Election Creation Process
Elections require unique names and admin passwords. The system generates SHA-256 password hashes for security.

```python
# Database structure for elections
Elections: {
    id: INTEGER PRIMARY KEY,
    name: TEXT UNIQUE,
    admin_password_hash: TEXT,
    created_at: TIMESTAMP
}
```

#### Candidate Management
- **Name Requirements**: Unicode support, no length restrictions
- **Symbol Management**: Optional image files with automatic scaling
- **Storage Method**: File path references with existence validation

### Voting Interface Technical Details

#### Security Implementation
- **Full-screen Mode**: `attributes('-fullscreen', True)` with topmost priority
- **System Key Blocking**: X11 xmodmap commands disable Super/Windows keys
- **Process Protection**: Window close events intercepted and blocked
- **Emergency Exit**: Ctrl+Q combination requires admin password verification

#### User Interaction Flow
1. **Candidate Selection**: Visual feedback with color state changes (red → green)
2. **Vote Casting**: Enter key triggers database insertion with timestamp
3. **Confirmation Display**: "BALLOT CAST" screen with visual checkmark
4. **Next Ballot**: Space key resets interface for subsequent voter

#### Audio Feedback System
Multi-tier audio implementation for maximum compatibility:
```bash
Priority 1: WAV generation + aplay (Ubuntu optimized)
Priority 2: PulseAudio bell sample
Priority 3: Terminal bell character fallback
```

### Database Operations

#### Vote Recording
```sql
INSERT INTO Votes (election_id, candidate_id, timestamp) 
VALUES (?, ?, CURRENT_TIMESTAMP)
```

#### Results Calculation
```sql
SELECT c.name, COUNT(v.id) as votes, 
       (COUNT(v.id) * 100.0 / ?) as percentage
FROM Candidates c
LEFT JOIN Votes v ON c.id = v.candidate_id
WHERE c.election_id = ?
GROUP BY c.id, c.name
ORDER BY votes DESC
```

## Database Schema

### Entity Relationship Design

#### Elections Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique election identifier |
| `name` | TEXT | NOT NULL UNIQUE | Human-readable election name |
| `admin_password_hash` | TEXT | NOT NULL | SHA-256 hashed admin password |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Election creation timestamp |

#### Candidates Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique candidate identifier |
| `election_id` | INTEGER | NOT NULL, FOREIGN KEY | Reference to parent election |
| `name` | TEXT | NOT NULL | Candidate display name |
| `symbol_path` | TEXT | NULLABLE | File system path to symbol image |
| `is_nota` | INTEGER | DEFAULT 0 | NOTA flag (1 for auto-generated NOTA) |

#### Votes Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique vote identifier |
| `election_id` | INTEGER | NOT NULL, FOREIGN KEY | Reference to election |
| `candidate_id` | INTEGER | NOT NULL, FOREIGN KEY | Reference to selected candidate |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Vote casting timestamp |

### Referential Integrity
- **CASCADE DELETE**: Election deletion removes all associated candidates and votes
- **FOREIGN KEY ENFORCEMENT**: `PRAGMA foreign_keys = ON` enforced at connection level
- **Transaction Safety**: All operations wrapped in database transactions

## Security Features

### Authentication System
- **Hash Algorithm**: SHA-256 with UTF-8 encoding
- **Storage Policy**: Plain text passwords never stored or logged
- **Verification**: Constant-time comparison prevents timing attacks

### Voting Security Measures
- **Kiosk Mode Implementation**: Full-screen window with system integration blocking
- **Key Interception**: X11 key mapping modification during voting sessions
- **Process Isolation**: Window manager integration prevention
- **Admin Override**: Secure exit mechanism with password verification

### Data Protection
- **Database Isolation**: SQLite file-based storage with local access only
- **Input Sanitization**: All user inputs validated and escaped
- **File System Security**: Controlled access to symbol and export directories

## Export Formats

### JSON Export Structure
```json
{
  "election_name": "Student Council Election",
  "total_votes": 247,
  "timestamp": "20250809_143022",
  "results": [
    {
      "candidate": "Alice Johnson",
      "votes": 123,
      "percentage": 49.80,
      "symbol_path": "/path/to/symbols/alice.png"
    },
    {
      "candidate": "Bob Williams", 
      "votes": 89,
      "percentage": 36.03,
      "symbol_path": "/path/to/symbols/bob.png"
    },
    {
      "candidate": "NOTA",
      "votes": 35,
      "percentage": 14.17,
      "symbol_path": null
    }
  ]
}
```

### CSV Export Format
Standard comma-separated values with UTF-8 encoding:
```csv
Candidate,Votes,Percentage
Alice Johnson,123,49.80
Bob Williams,89,36.03
NOTA,35,14.17
```

### PDF Report Features
- **Professional Layout**: A4 page format with proper margins and spacing
- **Corporate Styling**: Dark blue headers, alternating row backgrounds
- **Symbol Integration**: Embedded candidate symbols with automatic scaling
- **Metadata Inclusion**: Election name, generation timestamp, vote totals
- **Table Formatting**: Structured presentation with ranking and statistics

### File Naming Convention
All exports follow standardized naming:
```
{ElectionName}_{YYYYMMDD_HHMMSS}.{extension}
```

Examples:
- `Student_Council_2025_20250809_143022.json`
- `Class_President_20250809_143022.csv`
- `Grade_Representative_20250809_143022.pdf`

## Configuration

### Directory Structure
```
Election/
├── setup.sh                 # Automated installation script
├── run.py                   # Application entry point
├── election_app/            # Main application package
│   ├── __init__.py         # Package initialization
│   ├── db.py               # Database management
│   ├── main.py             # UI and application logic
│   ├── voting.py           # Voting interface
│   ├── dialogs.py          # Dialog components
│   ├── security.py         # Security functions
│   └── exporter.py         # Export functionality
├── symbols/                 # Candidate symbol storage
├── results/                 # Export output directory
├── venv/                   # Python virtual environment
├── election.db             # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

### Environment Configuration
```bash
# Optional: Custom database location
export ELECTION_DB_PATH="/custom/path/election.db"

# Optional: Custom symbols directory
export SYMBOLS_DIR="/custom/symbols/path"

# Optional: Custom results export directory
export RESULTS_DIR="/custom/results/path"

# Debug mode activation
export ELECTION_DEBUG=1
```

### Audio System Configuration
The application implements a three-tier audio feedback system:

1. **Primary Backend**: WAV file generation with ALSA playback
2. **Secondary Backend**: PulseAudio bell sample playback
3. **Fallback Backend**: ASCII bell character output

Audio dependencies (Ubuntu):
```bash
sudo apt install alsa-utils pulseaudio-utils
```

## Screenshots

### Main Application Interface
<img width="1142" height="713" alt="image" src="https://github.com/user-attachments/assets/ba998d80-38a5-434b-8232-be50d514c9be" />

- Main window with elections list and candidate management panels
- Election creation dialog with name and password fields
- Candidate add/edit dialog with symbol selection

### Voting Interface
<img width="1280" height="687" alt="image" src="https://github.com/user-attachments/assets/8e6c75ea-2a19-47eb-af37-b4d74f2c6636" />


- Full-screen voting interface with candidate selection buttons
- Vote confirmation screen with checkmark indicator
- Results viewing window with vote counts and percentages
(it does not allow taking screenshots. I have made it pretty secure, however it is far from fullproof)

### Export Examples

```
{
  "election_name": "GVHSS Panamaram 9D",
  "total_votes": 7,
  "timestamp": "20250809_231546",
  "results": [
    {
      "candidate": "Rahul",
      "votes": 2,
      "percentage": 28.57,
      "symbol_path": "/media/harikrishnanr/storage/Code/Election/symbols/pencil.png"
    },
    {
      "candidate": "Adil",
      "votes": 2,
      "percentage": 28.57,
      "symbol_path": "/media/harikrishnanr/storage/Code/Election/symbols/umbrella.png"
    },
    {
      "candidate": "Alex",
      "votes": 2,
      "percentage": 28.57,
      "symbol_path": "/media/harikrishnanr/storage/Code/Election/symbols/fan.png"
    },
    {
      "candidate": "NOTA",
      "votes": 1,
      "percentage": 14.29,
      "symbol_path": null
    }
  ]
}
```
- JSON structure in text editor showing hierarchical data
  
<img width="944" height="800" alt="image" src="https://github.com/user-attachments/assets/528b3350-bae3-4c91-adcd-1a992521875d" />


- PDF report sample with embedded symbols and professional formatting

```
Candidate,Votes,Percentage
Rahul,2,28.57
Adil,2,28.57
Alex,2,28.57
NOTA,1,14.29
```

- CSV export displayed in spreadsheet application


## Technical Implementation Details

### Database Design Patterns
- **Connection Pooling**: Thread-safe connection management with timeout handling
- **Schema Migration**: Automatic database schema updates for backward compatibility
- **Transaction Management**: Atomic operations with rollback capability
- **Foreign Key Enforcement**: Referential integrity maintained at database level

### GUI Framework Implementation
- **Tkinter Enhancement**: Custom styling with modern color schemes and typography
- **Layout Management**: Responsive design using pack and grid geometry managers
- **Event Handling**: Comprehensive keyboard and mouse event processing
- **Widget Customization**: Custom button states and visual feedback systems

### Image Processing Pipeline
```python
# Symbol processing workflow
1. Image file validation and format detection
2. RGBA conversion for transparency support
3. Proportional scaling with aspect ratio preservation
4. Canvas-based composition with centered positioning
5. ImageTk conversion for Tkinter compatibility
```

### Security Architecture
- **Password Hashing**: SHA-256 with UTF-8 encoding
- **Session Management**: Admin authentication per election access
- **System Integration**: X11 key mapping manipulation for kiosk mode
- **Process Protection**: Window manager interaction prevention

## Usage Guide

### Administrative Operations

#### Election Lifecycle Management
1. **Creation**: Unique name assignment with admin password configuration
2. **Access Control**: Password verification required for election modification
3. **Candidate Management**: Add, edit, delete operations with immediate UI updates
4. **Voting Execution**: Secure kiosk mode with audio feedback
5. **Results Export**: Multi-format report generation with timestamp tracking
6. **Data Cleanup**: Optional vote clearing with confirmation prompts

#### Candidate Symbol Management
- **Supported Formats**: PNG (recommended), JPG, JPEG, GIF, BMP
- **Automatic Processing**: Scaling, centering, and format conversion
- **Storage Strategy**: File path references with existence validation
- **Display Optimization**: Square canvas with transparency preservation

### Voting Process Technical Flow

#### Interface State Management
- **Selection State**: Single candidate selection with visual feedback
- **Vote State**: Confirmation required before database commitment
- **Completion State**: Success display with next ballot preparation
- **Error Handling**: Invalid operations blocked with user feedback

#### Keyboard Control Scheme
| Key Combination | Function | Access Level |
|-----------------|----------|--------------|
| `Enter` | Cast vote for selected candidate | Voter |
| `Space` | Advance to next ballot | Voting Officer |
| `Tab` | Delete most recent vote | Voting Officer |
| `Ctrl+Q` | Exit voting mode | Admin (password required) |
| `Escape` | Blocked (security measure) | None |
| `Alt+Tab` | Blocked (security measure) | None |

## Export Formats

### JSON Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "election_name": {"type": "string"},
    "total_votes": {"type": "integer"},
    "timestamp": {"type": "string", "pattern": "^[0-9]{8}_[0-9]{6}$"},
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "candidate": {"type": "string"},
          "votes": {"type": "integer"},
          "percentage": {"type": "number"},
          "symbol_path": {"type": ["string", "null"]}
        }
      }
    }
  }
}
```

### PDF Report Specifications
- **Page Format**: A4 (210 × 297 mm)
- **Margins**: 18mm on all sides
- **Font Family**: Helvetica (system font)
- **Header**: Election name with 24pt bold typography
- **Table Layout**: Rank, Name, Votes, Percentage, Symbol columns
- **Symbol Display**: 0.6" × 0.4" embedded images with scaling

### CSV Compatibility
- **Encoding**: UTF-8 with BOM for Excel compatibility
- **Delimiter**: Comma separation with quote escaping
- **Headers**: Standard column names for database import
- **Numeric Format**: Percentage values with 2 decimal precision

## Troubleshooting

### Common Installation Issues

#### Python Dependencies
```bash
# Error: No module named 'PIL'
pip install Pillow

# Error: Microsoft Visual C++ required (Windows)
pip install --upgrade setuptools wheel

# Error: Failed building wheel for some-package
sudo apt install python3-dev build-essential
```

#### Database Access Problems
```bash
# Database locked error
sudo chown $USER:$USER election.db
chmod 644 election.db

# Schema corruption
rm election.db  # Database will be recreated on next launch
```

#### Audio System Issues
```bash
# No audio feedback (Ubuntu)
sudo apt install alsa-utils pulseaudio-utils

# Test audio functionality
aplay /usr/share/sounds/alsa/Front_Left.wav

# PulseAudio service restart
systemctl --user restart pulseaudio
```

### Voting Interface Problems

#### Kiosk Mode Exit Issues
If the voting interface becomes unresponsive:
1. Attempt normal exit: `Ctrl+Q` → enter admin password
2. Switch to TTY: `Ctrl+Alt+F2`
3. Kill process: `pkill -f election_app`
4. Return to GUI: `Ctrl+Alt+F7`
5. Restart application if needed

#### System Key Restoration
```bash
# Manual key restoration if automatic restoration fails
xmodmap -e 'keycode 133=Super_L'
xmodmap -e 'keycode 134=Super_R' 
xmodmap -e 'add mod4 = Super_L Super_R'
```

### Performance Optimization

#### Large Candidate Lists
- **Scrolling**: Automatic scrollbar activation for >6 candidates
- **Memory Management**: Lazy image loading for symbol processing
- **Database Indexing**: Optimized queries for vote counting operations

#### System Resource Management
- **Memory Usage**: Typical consumption 50-100MB during normal operation
- **CPU Usage**: Minimal during idle, brief spikes during image processing
- **Disk I/O**: Periodic database writes, batch export operations

## Development

### Code Architecture Principles
- **Separation of Concerns**: Clear module boundaries with single responsibilities
- **Error Handling**: Comprehensive exception management with user feedback
- **Type Safety**: Implicit typing with defensive programming practices
- **Resource Management**: Proper cleanup of database connections and GUI resources

### Testing Procedures
```bash
# Manual testing checklist
1. Election creation with various name formats
2. Candidate addition with different image types
3. Voting session with multiple ballots
4. Results export in all formats
5. Password authentication edge cases
6. Database integrity after operations
```

### Extension Points
- **Custom Export Formats**: Extend `ResultsExporter` class
- **Authentication Methods**: Replace `SecurityManager` implementation
- **UI Themes**: Modify color schemes in main UI components
- **Audio Systems**: Add platform-specific audio backends

## Contributing

### Development Environment Setup
```bash
git clone https://github.com/Pixelrick420/Election.git
cd Election
python3 -m venv dev_env
source dev_env/bin/activate
pip install -r requirements.txt
```

### Code Standards
- **Style Guide**: PEP 8 compliance with 88-character line limits
- **Documentation**: Docstrings for all public methods and classes
- **Error Handling**: Explicit exception handling with user-friendly messages
- **Threading**: Thread-safe database operations with proper locking

### Contribution Workflow
1. Fork repository on GitHub
2. Create feature branch with descriptive name
3. Implement changes with appropriate testing
4. Ensure code style compliance
5. Submit pull request with detailed description

This software is free to use, share, and modify. No license restrictions apply. Users may distribute and modify the code for any purpose, including commercial applications.

## Repository Information

**GitHub Repository**: https://github.com/Pixelrick420/Election

**Installation Script**: The `setup.sh` script provides automated installation for Ubuntu 22.04 systems. Download and execute for complete system setup including all dependencies and configuration.
