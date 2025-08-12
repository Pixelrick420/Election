#!/bin/bash

# Election Management System - Automated Setup Script
# Compatible with Ubuntu 22.04
# Author: Election Management System Team
# Repository: https://github.com/Pixelrick420/Election

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Pixelrick420/Election.git"
PROJECT_DIR="Election"
PYTHON_VERSION="3.10"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if package is installed
package_installed() {
    dpkg -l | grep -q "^ii  $1 "
}

# Function to update package lists
update_packages() {
    print_status "Updating package lists..."
    print_status "This may take a moment, please wait..."
    sudo apt update -qq
    print_success "Package lists updated"
}

# Function to install git
install_git() {
    if command_exists git; then
        print_success "Git is already installed"
        git --version
    else
        print_status "Installing Git..."
        print_status "Downloading and installing git package..."
        sudo apt install -y git
        print_success "Git installed successfully"
        git --version
    fi
}

# Function to install Python
install_python() {
    if command_exists python3; then
        CURRENT_PYTHON=$(python3 --version | cut -d' ' -f2)
        print_success "Python3 is already installed (version: $CURRENT_PYTHON)"
    else
        print_status "Installing Python3..."
        print_status "Downloading and installing python3 package..."
        sudo apt install -y python3
        print_success "Python3 installed successfully"
    fi
    
    # Check for python3-pip
    if command_exists pip3; then
        print_success "pip3 is already installed"
    else
        print_status "Installing pip3..."
        print_status "Downloading and installing python3-pip package..."
        sudo apt install -y python3-pip
        print_success "pip3 installed successfully"
    fi
    
    # Check for python3-venv
    if package_installed python3-venv; then
        print_success "python3-venv is already installed"
    else
        print_status "Installing python3-venv..."
        print_status "Downloading and installing python3-venv package..."
        sudo apt install -y python3-venv
        print_success "python3-venv installed successfully"
    fi
    
    # Install python3-dev for building packages
    if package_installed python3-dev; then
        print_success "python3-dev is already installed"
    else
        print_status "Installing python3-dev (required for some packages)..."
        print_status "Downloading and installing python3-dev package..."
        sudo apt install -y python3-dev
        print_success "python3-dev installed successfully"
    fi
    
    # Install build essentials (required for bcrypt and other packages)
    if package_installed build-essential; then
        print_success "build-essential is already installed"
    else
        print_status "Installing build-essential (required for compiling packages)..."
        print_status "This is a larger package and may take a few minutes..."
        sudo apt install -y build-essential
        print_success "build-essential installed successfully"
    fi
}

# Function to install tkinter
install_tkinter() {
    if package_installed python3-tk; then
        print_success "python3-tk (tkinter) is already installed"
    else
        print_status "Installing python3-tk (tkinter GUI library)..."
        print_status "Downloading and installing tkinter package..."
        sudo apt install -y python3-tk
        print_success "python3-tk installed successfully"
    fi
    
    # Test tkinter installation
    print_status "Testing tkinter installation..."
    if python3 -c "import tkinter; print('Tkinter test successful')" 2>/dev/null; then
        print_success "Tkinter is working correctly"
    else
        print_error "Tkinter installation test failed!"
        print_status "This may cause GUI issues. Please check your installation."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to clone repository
clone_repository() {
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Directory '$PROJECT_DIR' already exists"
        read -p "Do you want to remove it and clone fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing directory..."
            rm -rf "$PROJECT_DIR"
        else
            print_status "Using existing directory..."
            cd "$PROJECT_DIR"
            return 0
        fi
    fi
    
    print_status "Cloning Election Management System repository..."
    print_status "Downloading source code from GitHub..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    print_success "Repository cloned successfully"
    cd "$PROJECT_DIR"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf venv
        else
            print_status "Using existing virtual environment..."
            return 0
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created successfully"
}

# Function to activate virtual environment and install requirements
install_requirements() {
    print_status "Activating virtual environment and installing requirements..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip first
    print_status "Upgrading pip to latest version..."
    print_status "This ensures compatibility with all packages..."
    pip install --upgrade pip
    print_success "pip upgraded successfully"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt not found, creating basic requirements..."
        cat > requirements.txt << EOF
bcrypt==4.1.2
Pillow==10.2.0
EOF
    fi
    
    # Install requirements
    print_status "Installing Python packages from requirements.txt..."
    print_status "Installing bcrypt (password hashing library)..."
    print_status "Installing Pillow (image processing library)..."
    print_status "This may take a few minutes as packages are compiled..."
    pip install -r requirements.txt
    
    print_success "All requirements installed successfully"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if main files exist
    required_files=("run.py" "election_app/__init__.py" "election_app/ui.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file '$file' not found!"
            return 1
        fi
    done
    
    # Check if symbols directory exists
    if [ ! -d "symbols" ]; then
        print_warning "Symbols directory not found, creating it..."
        mkdir -p symbols
    fi
    
    # Check if results directory exists
    if [ ! -d "results" ]; then
        print_status "Creating results directory..."
        mkdir -p results
    fi
    
    print_success "Installation verification completed"
}

# Function to create desktop shortcut
create_shortcut() {
    read -p "Do you want to create a desktop shortcut? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DESKTOP_DIR="$HOME/Desktop"
        if [ -d "$DESKTOP_DIR" ]; then
            SHORTCUT_PATH="$DESKTOP_DIR/Election Management System.desktop"
            CURRENT_DIR=$(pwd)
            
            cat > "$SHORTCUT_PATH" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Election
Comment=Electronic Voting System
Exec=bash -c "cd '$CURRENT_DIR' && source venv/bin/activate && python3 run.py"
Icon=$CURRENT_DIR/elections.png
Terminal=false
StartupNotify=true
Categories=Office;
EOF
            
            chmod +x "$SHORTCUT_PATH"
            print_success "Desktop shortcut created at '$SHORTCUT_PATH'"
        else
            print_warning "Desktop directory not found, skipping shortcut creation"
        fi
    fi
}

# Function to run the application
run_application() {
    print_status "Setup completed successfully!"
    echo
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN} Election Management System${NC}"
    echo -e "${GREEN}================================${NC}"
    echo
    echo -e "Installation directory: ${BLUE}$(pwd)${NC}"
    echo -e "To run the application manually:"
    echo -e "  ${YELLOW}cd $(pwd)${NC}"
    echo -e "  ${YELLOW}source venv/bin/activate${NC}"
    echo -e "  ${YELLOW}python3 run.py${NC}"
    echo
    
    read -p "Do you want to run the Election Management System now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_status "Starting Election Management System..."
        source venv/bin/activate
        python3 run.py
    else
        print_success "Setup completed. You can run the application later using the commands above."
    fi
}

# Function to handle cleanup on error
cleanup_on_error() {
    print_error "An error occurred during setup!"
    print_status "Cleaning up..."
    
    if [ -d "$PROJECT_DIR" ]; then
        read -p "Do you want to remove the partially installed directory '$PROJECT_DIR'? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
            print_status "Cleanup completed"
        fi
    fi
    
    exit 1
}

# Main installation function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} Election Management System${NC}"
    echo -e "${BLUE} Automated Setup Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    echo -e "This script will install and setup the Election Management System"
    echo -e "Repository: ${YELLOW}$REPO_URL${NC}"
    echo -e "Target System: ${YELLOW}Ubuntu 22.04${NC}"
    echo
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "Please do not run this script as root!"
        print_status "Run it as a regular user. The script will ask for sudo password when needed."
        exit 1
    fi
    
    # Check Ubuntu version
    if ! grep -q "22.04" /etc/os-release 2>/dev/null; then
        print_warning "This script is designed for Ubuntu 22.04"
        print_warning "Your system might be different. Continue anyway?"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Trap errors for cleanup
    trap cleanup_on_error ERR
    
    print_status "Starting installation process..."
    echo
    
    # Step 1: Update packages
    update_packages
    echo
    
    # Step 2: Install dependencies
    install_git
    echo
    install_python
    echo
    install_tkinter
    echo
    
    # Step 3: Clone repository
    clone_repository
    echo
    
    # Step 4: Setup virtual environment
    setup_venv
    echo
    
    # Step 5: Install requirements
    install_requirements
    echo
    
    # Step 6: Verify installation
    verify_installation
    echo
    
    # Step 7: Create shortcut (optional)
    create_shortcut
    echo
    
    # Step 8: Run application
    run_application
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi