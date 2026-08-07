#!/usr/bin/env bash

set -e

############################################################
# Colors
############################################################
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN=$'\033[0;36m'
MAGENTA="\033[0;35m"
WHITE=$'\033[1;37m'
NC=$'\033[0m'


WHITE=$'\033[1;37m'
CYAN=$'\033[0;36m'
NC=$'\033[0m'

############################################
# Helper Functions
############################################

info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $1"
}

error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

############################################
# Check Linux
############################################

if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    error "This installer only supports Linux."
    exit 1
fi


############################################################
# Banner
############################################################
clear

echo -e "${WHITE}╔═════════════════════════════════════════════════════════════════╗${NC}"
#echo -e "${WHITE}╔════════════════════════════════════════════════════╗${NC}"

#echo -e "${CYAN}"
{
figlet -c "   Laser                  "
figlet -c "Scanner        "
echo "---------------------------------------------------------------"
echo -e "${GREEN} Project Name :${NC} Laser Scanner                                  "
echo "                                                               "
echo -e "${GREEN} Company      :${NC} Nirad Mechatronics                             "
echo "                                                               "
echo -e "${GREEN} Developer    :${NC} AmirMohammad Abolhasani (AmirCodeNinjaX)       "
echo -e "                https://github.com/AmirCodeNinjaX              "
echo "                                                               "
echo -e "${GREEN} Manager      :${NC} Amir Mohammadi (Hoodie-Boy)                    "
echo -e "                https://github.com/Hoodie-Boy                  " 
} | sed '/^*$/d; s/^/'"${WHITE}"'║'"${CYAN}"' /; s/$/ '"${WHITE}"'║'"${CYAN}"'/'

# figlet "SCANNER                                              " | sed '/^[[:space:]]*$/d; s/^/'"${WHITE}"'║'"${CYAN}"' /; s/$/ '"${WHITE}"'║'"${CYAN}"'/'

#echo -e "${NC}"
#echo -e "${WHITE}╚═════════════════════════════════════════════════════════════════╝${NC}"


echo -e "${WHITE}╚═════════════════════════════════════════════════════════════════╝${NC}"
echo


############################################################
# Confirmation
############################################################

echo
echo -e "${CYAN}This installer will:${NC}"
echo "  • Check your operating system"
echo "  • Verify required system packages"
echo "  • Install missing dependencies (with your permission)"
echo "  • Create a Python virtual environment"
echo "  • Install all Python requirements"
echo

read -rp "Continue with the setup? [Y/n]: " START_SETUP
START_SETUP=${START_SETUP:-Y}

if [[ ! "$START_SETUP" =~ ^[Yy]$ ]]; then
    echo
    echo -e "${YELLOW}Setup cancelled by user.${NC}"
    echo -e "${CYAN}Thank you for using Laser Scanner Installer! 👋${NC}"
    exit 0
fi

echo
success "Starting installation..."
echo

############################################################
# Raspberry Pi Check
############################################################

info "Checking Raspberry Pi hardware..."

if [[ -f /proc/device-tree/model ]]; then

    RPI_MODEL=$(cat /proc/device-tree/model)

    if [[ "$RPI_MODEL" == *"Raspberry Pi"* ]]; then
        success "Raspberry Pi detected:"
        echo -e "         ${CYAN}$RPI_MODEL${NC}"
        echo
    else
        error "Unsupported hardware detected!"
        echo
        echo -e "${YELLOW}This project only supports Raspberry Pi devices.${NC}"
        echo -e "${WHITE}Detected device:${NC} $RPI_MODEL"
        echo
        read -n 1 -s -r -p "Press any key to abort..."
        echo
        exit 1
    fi

else
    error "Cannot detect Raspberry Pi hardware."
    echo
    echo -e "${YELLOW}This installer can only run on Raspberry Pi.${NC}"
    echo
    read -n 1 -s -r -p "Press any key to abort..."
    echo
    exit 1
fi

success "Hardware verification completed."
echo


############################################
# Detect Package Manager
############################################

if command -v apt >/dev/null 2>&1; then
    PKG_MANAGER="apt"
    LIBCAP_PACKAGE="libcap-dev"

elif command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
    LIBCAP_PACKAGE="libcap"

elif command -v yum >/dev/null 2>&1; then
    PKG_MANAGER="yum"
    LIBCAP_PACKAGE="libcap"

elif command -v pacman >/dev/null 2>&1; then
    PKG_MANAGER="pacman"
    LIBCAP_PACKAGE="libcap"

else
    error "Unsupported package manager."
    exit 1
fi

############################################
# Check if libcap is installed
############################################

if command -v setcap >/dev/null 2>&1; then
    success "libcap is already installed."
else
    warning "libcap is required but not installed."

    read -rp "Install it now? [Y/n]: " answer
    answer=${answer:-Y}

    if [[ "$answer" =~ ^[Yy]$ ]]; then

        info "Installing libcap..."

        case $PKG_MANAGER in

            apt)
                sudo apt update
                sudo apt install -y "$LIBCAP_PACKAGE"
                ;;

            dnf)
                sudo dnf install -y "$LIBCAP_PACKAGE"
                ;;

            yum)
                sudo yum install -y "$LIBCAP_PACKAGE"
                ;;

            pacman)
                sudo pacman -Sy --noconfirm "$LIBCAP_PACKAGE"
                ;;

        esac

        success "libcap installed."

    else
        error "Cannot continue without libcap."
        exit 1
    fi
fi

############################################
# Install Python Requirements
############################################

info "Creating virtual environment..."

python3 -m venv .venv

source .venv/bin/activate

success "Virtual environment created."

info "Installing Python dependencies..."

python -m pip install --upgrade pip
python -m pip install -r ./Image_Processing_Code/requirements.txt
echo
success "Python dependencies installed."

############################################
# Finished
############################################

echo
success "Installation completed successfully!"
echo

echo "You can now use"
