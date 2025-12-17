#!/usr/bin/env python3
"""
Unified launcher for AIT Search Engine.
Starts both backend API and frontend server simultaneously.
"""
import subprocess
import sys
import os
import time
import signal
import webbrowser
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def print_banner():
    print_colored("\n" + "="*60, Colors.BLUE)
    print_colored("🚀 AIT Search Engine - Unified Launcher", Colors.BOLD)
    print_colored("="*60 + "\n", Colors.BLUE)

# Global process holders
backend_process = None
frontend_process = None

def cleanup(signum=None, frame=None):
    """Cleanup function to kill both servers"""
    print_colored("\n\n🛑 Shutting down servers...", Colors.YELLOW)
    
    if backend_process:
        print_colored("   Stopping backend server...", Colors.YELLOW)
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
    
    if frontend_process:
        print_colored("   Stopping frontend server...", Colors.YELLOW)
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
    
    print_colored("\n✅ Servers stopped successfully!", Colors.GREEN)
    sys.exit(0)

def start_backend():
    """Start the FastAPI backend server"""
    global backend_process
    
    backend_dir = Path(__file__).parent / "backend"
    
    print_colored("📡 Starting backend API server...", Colors.BLUE)
    print_colored(f"   Directory: {backend_dir}", Colors.BLUE)
    print_colored("   URL: http://localhost:8000", Colors.BLUE)
    print_colored("   Docs: http://localhost:8000/docs\n", Colors.BLUE)
    
    # Start uvicorn
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return backend_process

def start_frontend():
    """Start the frontend HTTP server"""
    global frontend_process
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    print_colored("🌐 Starting frontend server...", Colors.BLUE)
    print_colored(f"   Directory: {frontend_dir}", Colors.BLUE)
    print_colored("   URL: http://localhost:8080\n", Colors.BLUE)
    
    # Start simple HTTP server
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return frontend_process

def wait_for_backend():
    """Wait for backend to be ready"""
    import urllib.request
    import urllib.error
    
    print_colored("⏳ Waiting for backend to initialize...", Colors.YELLOW)
    
    max_attempts = 60  # 60 seconds
    for i in range(max_attempts):
        try:
            urllib.request.urlopen("http://localhost:8000/api/", timeout=1)
            print_colored("✅ Backend is ready!\n", Colors.GREEN)
            return True
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
            time.sleep(1)
            if i % 5 == 0:
                print_colored(f"   Still waiting... ({i}s)", Colors.YELLOW)
    
    print_colored("❌ Backend failed to start within 60 seconds", Colors.RED)
    return False

def print_stream(process, prefix, color):
    """Print output from subprocess with prefix"""
    try:
        for line in process.stdout:
            if line.strip():
                print(f"{color}{prefix}{Colors.ENDC} {line.strip()}")
    except:
        pass

def main():
    # Register cleanup handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    print_banner()
    
    try:
        # Start backend
        backend_proc = start_backend()
        
        # Wait for backend to be ready
        if not wait_for_backend():
            cleanup()
            return
        
        # Start frontend
        frontend_proc = start_frontend()
        time.sleep(2)  # Give frontend time to start
        
        print_colored("="*60, Colors.GREEN)
        print_colored("✅ Both servers are running!", Colors.GREEN)
        print_colored("="*60, Colors.GREEN)
        print()
        print_colored("📍 Access Points:", Colors.BOLD)
        print_colored("   Frontend:  http://localhost:8080", Colors.BLUE)
        print_colored("   Backend:   http://localhost:8000", Colors.BLUE)
        print_colored("   API Docs:  http://localhost:8000/docs", Colors.BLUE)
        print()
        print_colored("💡 Press Ctrl+C to stop both servers", Colors.YELLOW)
        print_colored("="*60 + "\n", Colors.GREEN)
        
        # Open browser
        try:
            time.sleep(1)
            webbrowser.open("http://localhost:8080")
            print_colored("🌐 Browser opened automatically!\n", Colors.GREEN)
        except:
            print_colored("⚠️  Could not open browser automatically", Colors.YELLOW)
            print_colored("   Please open http://localhost:8080 manually\n", Colors.YELLOW)
        
        # Keep running and monitor processes
        print_colored("📋 Server Logs:\n", Colors.BOLD)
        
        # Monitor both processes
        while True:
            # Check if processes are still running
            if backend_proc.poll() is not None:
                print_colored("❌ Backend server stopped unexpectedly!", Colors.RED)
                cleanup()
                break
            
            if frontend_proc.poll() is not None:
                print_colored("❌ Frontend server stopped unexpectedly!", Colors.RED)
                cleanup()
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print_colored(f"\n❌ Error: {str(e)}", Colors.RED)
        cleanup()

if __name__ == "__main__":
    main()
