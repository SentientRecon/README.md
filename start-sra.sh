#!/bin/bash

# Sentient Recon Agent (SRA) Startup Script
# This script helps you get the SRA platform running quickly

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Logo
print_logo() {
    echo -e "${CYAN}"
    cat << "EOF"
    ███████╗██████╗  █████╗ 
    ██╔════╝██╔══██╗██╔══██╗
    ███████╗██████╔╝███████║
    ╚════██║██╔══██╗██╔══██║
    ███████║██║  ██║██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
    
    Sentient Recon Agent Platform
    Advanced Cybersecurity Operations
EOF
    echo -e "${NC}"
}

# Print colored output
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

print_header() {
    echo -e "\n${PURPLE}=== $1 ===${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=()
    
    # Check Node.js
    if command_exists node; then
        local node_version=$(node --version | cut -d'v' -f2)
        print_success "Node.js found: v$node_version"
        
        # Check if version is >= 18
        local major_version=$(echo $node_version | cut -d'.' -f1)
        if [ "$major_version" -lt 18 ]; then
            print_warning "Node.js version should be 18+ for best compatibility"
        fi
    else
        missing_deps+=("Node.js 18+")
    fi
    
    # Check npm
    if command_exists npm; then
        local npm_version=$(npm --version)
        print_success "npm found: v$npm_version"
    else
        missing_deps+=("npm")
    fi
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python found: v$python_version"
        
        # Check if version is >= 3.8
        local major_version=$(echo $python_version | cut -d'.' -f1)
        local minor_version=$(echo $python_version | cut -d'.' -f2)
        if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
            print_warning "Python version should be 3.8+ for best compatibility"
        fi
    else
        missing_deps+=("Python 3.8+")
    fi
    
    # Check pip
    if command_exists pip3; then
        local pip_version=$(pip3 --version | cut -d' ' -f2)
        print_success "pip found: v$pip_version"
    else
        missing_deps+=("pip3")
    fi
    
    # Check git
    if command_exists git; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_success "Git found: v$git_version"
    else
        missing_deps+=("git")
    fi
    
    # Report missing dependencies
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo -e "  ${RED}- $dep${NC}"
        done
        echo ""
        print_error "Please install missing dependencies and run this script again."
        exit 1
    fi
    
    print_success "All prerequisites satisfied!"
}

# Setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        
        # Generate a random secret key
        local secret_key=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 32)
        
        # Replace default secret key with generated one
        if command_exists sed; then
            sed -i.bak "s/your_super_secret_key_change_in_production/$secret_key/g" .env
            rm -f .env.bak
            print_success "Generated secure SECRET_KEY"
        fi
        
        print_warning "Please edit .env file to configure your specific settings"
        print_status "Important: Add your OpenAI API key for AI features"
    else
        print_success "Environment file already exists"
    fi
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    # Install root dependencies
    print_status "Installing root dependencies..."
    npm install
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    cd ..
    
    print_success "All dependencies installed successfully!"
}

# Setup database
setup_database() {
    print_header "Setting Up Database"
    
    cd backend
    source venv/bin/activate
    
    # Note: Database setup would go here when models are implemented
    print_status "Database setup will be implemented with SQLAlchemy models"
    print_success "Database configuration ready"
    
    cd ..
}

# Start development servers
start_development() {
    print_header "Starting Development Servers"
    
    print_status "Starting backend server (FastAPI)..."
    cd backend
    source venv/bin/activate
    
    # Start backend in background
    python -m uvicorn python_api.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    print_status "Starting frontend server (React)..."
    cd frontend
    
    # Start frontend in background
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Print access information
    echo ""
    print_success "🚀 SRA Platform is starting up!"
    echo ""
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  Frontend: ${CYAN}http://localhost:3000${NC}"
    echo -e "  Backend API: ${CYAN}http://localhost:8000${NC}"
    echo -e "  API Documentation: ${CYAN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}Default Login (Development):${NC}"
    echo -e "  Username: ${CYAN}admin${NC}"
    echo -e "  Password: ${CYAN}admin123${NC}"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop all servers${NC}"
    
    # Wait for user interrupt
    trap cleanup INT
    wait
}

# Cleanup function
cleanup() {
    print_header "Shutting Down"
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend server..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend server..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn python_api.main:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    print_success "Servers stopped. Goodbye! 👋"
    exit 0
}

# Production build
build_production() {
    print_header "Building for Production"
    
    # Build frontend
    print_status "Building frontend..."
    cd frontend
    npm run build
    cd ..
    
    # Prepare backend
    print_status "Preparing backend for production..."
    cd backend
    source venv/bin/activate
    
    # Install production dependencies
    pip install gunicorn
    
    cd ..
    
    print_success "Production build complete!"
    print_status "Frontend build: ./frontend/dist"
    print_status "Backend ready for: gunicorn python_api.main:app"
}

# Show help
show_help() {
    echo "SRA Platform Startup Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start development servers (default)"
    echo "  setup     Run initial setup only"
    echo "  build     Build for production"
    echo "  check     Check prerequisites only"
    echo "  clean     Clean dependencies and build files"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start development servers"
    echo "  $0 setup        # Run setup without starting servers"
    echo "  $0 build        # Build for production deployment"
}

# Clean dependencies and build files
clean_environment() {
    print_header "Cleaning Environment"
    
    print_status "Removing node_modules..."
    rm -rf node_modules frontend/node_modules backend/node_modules
    
    print_status "Removing Python virtual environment..."
    rm -rf backend/venv
    
    print_status "Removing build files..."
    rm -rf frontend/dist backend/dist
    
    print_status "Removing cache files..."
    rm -rf frontend/.vite backend/__pycache__ backend/python_api/__pycache__
    
    print_success "Environment cleaned!"
}

# Main execution
main() {
    print_logo
    
    case "${1:-start}" in
        "start")
            check_prerequisites
            setup_environment
            install_dependencies
            setup_database
            start_development
            ;;
        "setup")
            check_prerequisites
            setup_environment
            install_dependencies
            setup_database
            print_success "Setup complete! Run './start-sra.sh start' to launch servers."
            ;;
        "build")
            check_prerequisites
            install_dependencies
            build_production
            ;;
        "check")
            check_prerequisites
            ;;
        "clean")
            clean_environment
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"