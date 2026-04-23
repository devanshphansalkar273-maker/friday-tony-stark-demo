#!/usr/bin/env python3
"""
PDF Equation Solver - Setup and Verification Script

Automatically installs dependencies and verifies the setup is complete.
"""

import subprocess
import sys
import json
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_step(step: int, text: str):
    """Print a numbered step."""
    print(f"\n[{step}] {text}")


def print_success(text: str):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"✗ {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"⚠ {text}")


def install_python_packages():
    """Install required Python packages."""
    print_step(1, "Installing Python packages")
    
    packages = [
        "PyPDF2>=3.0.0",
        "sympy>=1.12",
        "python-docx>=0.8.11",
        "ollama>=0.0.11"
    ]
    
    for package in packages:
        print(f"  Installing {package}...", end=" ")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print_success("Done")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install {package}")
            return False
    
    return True


def verify_python_packages():
    """Verify all Python packages are installed."""
    print_step(2, "Verifying Python packages")
    
    packages = {
        "PyPDF2": "pdf_reader",
        "sympy": "equation_solver",
        "docx": "document_writer",
        "ollama": "llm_extraction"
    }
    
    all_installed = True
    
    for package, usage in packages.items():
        try:
            __import__(package.split(">=")[0])
            print_success(f"{package:20} → {usage}")
        except ImportError:
            print_error(f"{package:20} NOT FOUND")
            all_installed = False
    
    return all_installed


def check_ollama_installation():
    """Check if Ollama is installed."""
    print_step(3, "Checking Ollama installation")
    
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
            print_success(f"Ollama installed (version: {version})")
            return True
        else:
            print_error("Ollama command found but not working")
            return False
    
    except FileNotFoundError:
        print_error("Ollama is not installed")
        print("\nTo install Ollama:")
        print("  macOS: brew install ollama")
        print("  Linux: curl https://ollama.ai/install.sh | sh")
        print("  Windows: Download from https://ollama.ai/download")
        return False
    
    except subprocess.TimeoutExpired:
        print_error("Ollama check timed out")
        return False


def check_ollama_server():
    """Check if Ollama server is running."""
    print_step(4, "Checking Ollama server")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if models:
                print_success(f"Ollama server running with {len(models)} model(s)")
                for model in models:
                    name = model.get("name", "unknown").split(":")[0]
                    print(f"    • {name}")
                return True
            else:
                print_warning("Ollama server running but no models installed")
                print("  Run: ollama pull mistral")
                return False
        else:
            print_error(f"Ollama server returned status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Ollama server at http://localhost:11434")
        print("\nTo start Ollama server:")
        print("  1. In terminal 1: ollama serve")
        print("  2. In terminal 2: ollama pull mistral")
        print("  3. Keep terminal 1 running")
        return False
    
    except Exception as e:
        print_error(f"Error checking Ollama server: {e}")
        return False


def install_ollama_model():
    """Install Ollama model (mistral)."""
    print_step(5, "Installing Ollama model")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = response.json().get("models", [])
        
        for model in models:
            name = model.get("name", "").split(":")[0]
            if name in ["mistral", "neural-chat", "llama2"]:
                print_success(f"Model '{name}' already installed")
                return True
        
        # If no suitable model found, ask user to install
        print_warning("No suitable model found")
        print("\nTo install a model:")
        print("  ollama pull mistral      (recommended, lightweight)")
        print("  ollama pull neural-chat  (good accuracy)")
        print("  ollama pull llama2       (larger, more features)")
        return False
    
    except:
        print_warning("Could not check available models")
        print("  Run: ollama pull mistral")
        return False


def test_module_imports():
    """Test if PDF solver modules can be imported."""
    print_step(6, "Testing module imports")
    
    modules = [
        ("friday.system.pdf_reader", "PDFReader"),
        ("friday.system.equation_extractor", "EquationExtractor"),
        ("friday.system.solver", "EquationSolver"),
        ("friday.system.doc_writer", "DocumentWriter"),
        ("friday.system.pdf_solver", "PDFEquationSolver"),
    ]
    
    all_imported = True
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_success(f"{class_name:20} from {module_name}")
        except ImportError as e:
            print_error(f"Cannot import {module_name}")
            print(f"      Error: {e}")
            all_imported = False
        except AttributeError:
            print_error(f"Class {class_name} not found in {module_name}")
            all_imported = False
    
    return all_imported


def test_quick_solve():
    """Test quick equation solving."""
    print_step(7, "Testing equation solving")
    
    try:
        from friday.system.solver import EquationSolver
        
        solver = EquationSolver()
        result = solver.solve_equation("x + 2 = 5")
        
        if result["status"] == "success" and result["solutions"]:
            solutions = result["solutions"][0]
            print_success(f"Equation solved: x = {solutions.get('x', 'error')}")
            return True
        else:
            print_error("Equation solver returned no solutions")
            return False
    
    except Exception as e:
        print_error(f"Equation solving failed: {e}")
        return False


def generate_setup_report(results: dict):
    """Generate setup report."""
    print_header("SETUP REPORT")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"\nPassed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print_success("✓ Setup is complete and verified!")
        print("\nYou can now use the PDF Equation Solver:")
        print("  from friday.system.pdf_solver import solve_pdf")
        print("  result = solve_pdf('equations.pdf', 'solutions.docx')")
    
    else:
        print_warning("⚠ Some checks failed")
        print("\nFailed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  • {check}")
        
        print("\nNext steps:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Install model: ollama pull mistral")
        print("4. Run this script again to verify")
    
    print("\n" + "="*60)
    print("For documentation, see:")
    print("  • PDF_SOLVER_README.md - Full documentation")
    print("  • QUICK_START_PDF_SOLVER.py - Code examples")
    print("  • test_pdf_solver.py - 10 complete examples")
    print("="*60 + "\n")
    
    return passed_checks == total_checks


def main():
    """Run full setup and verification."""
    print_header("PDF EQUATION SOLVER - SETUP VERIFICATION")
    
    checks = {
        "Python packages installed": False,
        "Python packages verified": False,
        "Ollama installed": False,
        "Ollama server running": False,
        "Ollama model available": False,
        "Module imports working": False,
        "Equation solving works": False,
    }
    
    # Step 1: Install packages
    if install_python_packages():
        checks["Python packages installed"] = True
    else:
        print_error("Failed to install Python packages")
        print("Try installing manually:")
        print("  pip install PyPDF2 sympy python-docx ollama")
    
    # Step 2: Verify packages
    checks["Python packages verified"] = verify_python_packages()
    
    # Step 3: Check Ollama installation
    checks["Ollama installed"] = check_ollama_installation()
    
    # Step 4: Check Ollama server
    checks["Ollama server running"] = check_ollama_server()
    
    # Step 5: Check/install model
    checks["Ollama model available"] = install_ollama_model()
    
    # Step 6: Test imports
    if checks["Python packages verified"]:
        checks["Module imports working"] = test_module_imports()
    
    # Step 7: Test solving
    if checks["Module imports working"]:
        checks["Equation solving works"] = test_quick_solve()
    
    # Generate report
    success = generate_setup_report(checks)
    
    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
