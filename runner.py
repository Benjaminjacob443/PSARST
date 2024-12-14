import os
import subprocess
import sys
from pathlib import Path
import shutil
import datetime
import re
import logging
import platform

# ANSI escape codes
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"  # Reset color to default

# Constants
VENV_NAME = "psarst_env"  # Name of the virtual environment
REQUIREMENTS_FILE = "psarst_requirements.txt"
SCRIPT_PATH = "PSARST.py"  # Your main script path
PYTHON_VERSION = "3.11.1"  # Python version to use in the virtual environment
PYTHON_INSTALLER = "python-installer.exe"  # Python installer filename
LOGS_DIR = "logs"  # Folder to store logs

# Helper function to run shell commands
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[{RED} FAILED {RESET}] Error executing command: {command}\n{e}")
        logging.error(f"Error executing command: {command}\n{e}")
        sys.exit(1)

# Helper function to log errors
def setup_logging():
    try:
        # Get the path of the executable or script
        base_path = os.path.dirname(sys.argv[0])  # This works for both scripts and EXEs
        base_log_dir = os.path.join(base_path, 'logs', 'Error Logs')

        # Create the directories if they do not exist
        os.makedirs(base_log_dir, exist_ok=True)

        # Set up logging configuration
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"PSARST_{timestamp}.log"
        log_file_path = os.path.join(base_log_dir, log_filename)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file_path)]
        )

        # Log basic info
        python_version = sys.version.split()[0]
        current_os = platform.system()
        product_name = 'PSARST-BACKTESTING'
        date_time = datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')

        initial_message = f"""
Date                    : {date_time}
Python Version          : {python_version}
Current OS              : {current_os}
Time Zone               : IST | IST
Product Name            : {product_name}
"""

        logging.info(initial_message)
        print(f"[ {GREEN}OK{RESET} ] Logging setup Completed Successfully")
    
    except Exception as e:
        print(f"[ {RED}Failed{RESET} ] Failed to set up logging: {e}")
        logging.error(f"Failed to set up logging: {e}")
        raise

def venv_exists(venv_path):
    # For Windows
    if os.name == "nt":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        # For UNIX-like systems (Linux/Mac)
        python_path = venv_path / "bin" / "python"

    return python_path.exists()

def check_python_version(venv_path):
    python_path = venv_path / "Scripts" / "python.exe" if os.name == "nt" else venv_path / "bin" / "python"
    result = subprocess.run([python_path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        python_version = result.stdout.decode().strip().split()[1]
        if python_version == PYTHON_VERSION:
            return True
    return False

def dependencies_installed(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"
    
    def clean_version(version_str):
        # Remove any extra characters that might be part of the version
        return re.sub(r'[^0-9.]', '', version_str.strip())

    try:
        with open(REQUIREMENTS_FILE, "r") as f:
            requirements = f.readlines()

        for req in requirements:
            req = req.strip()
            if req:  # Skip empty lines
                # Skip ta-lib dependency checking entirely
                if "TA_Lib" in req:
                    continue  # Skip checking ta-lib and move to the next package

                # Check if the package is already installed
                result = subprocess.run(
                    [pip_path, "show", req.split("==")[0]],  # Only check the package name
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if result.returncode != 0:  # If package not found
                    print(f"[{RED} MISSING {RESET}] {req} is not installed.")
                    logging.error(f"{req} is not installed.")
                    return False
                else:
                    # Get the installed version from the 'pip show' output
                    installed_version = subprocess.run(
                        [pip_path, "show", req.split("==")[0]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    installed_version = installed_version.stdout.decode().strip().split('\n')[1].split(': ')[1]
                    installed_version = clean_version(installed_version)  # Clean the version string
                    
                    # Compare with required version if specified
                    if "==" in req:
                        required_version = req.split("==")[1]
                        required_version = clean_version(required_version)  # Clean the required version string
                        
                        if installed_version != required_version:
                            print(f"[{RED} VERSION MISMATCH {RESET}] {req} installed version {installed_version} doesn't match required {required_version}.")
                            logging.error(f"{req} installed version {installed_version} doesn't match required {required_version}.")
                            return False
                        else:
                            print(f"[{GREEN} OK {RESET}] {req} is already installed and up-to-date.")
                            logging.info(f"{req} is already installed and up-to-date.")
                    else:
                        print(f"[{GREEN} OK {RESET}] {req} is already installed (latest version).")
                        logging.info(f"{req} is already installed (latest version).")
        return True

    except FileNotFoundError:
        print(f"[{RED} FAILED {RESET}] Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
        logging.error(f"Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
        sys.exit(1)

def create_new_venv(venv_path):
    print(f"[{GREEN} -- {RESET}] Creating a new virtual environment at {venv_path}...")
    logging.info(f"Creating a new virtual environment at {venv_path}...")
    run_command(f"python -m venv {venv_path}")
    print(f"[{GREEN} OK {RESET}] New virtual environment created.")
    logging.info('New virtual environment created.')

def install_requirements(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"
    print(f"[{GREEN} -- {RESET}] Installing dependencies from {REQUIREMENTS_FILE}...")
    logging.info(f"Installing dependencies from {REQUIREMENTS_FILE}...")
    run_command(f"{pip_path} install -r {REQUIREMENTS_FILE}")
    print(f"[{GREEN} OK {RESET}] All dependencies installed.")
    logging.info(f"All dependencies installed.")

def install_python_in_venv(venv_path):
    python_installer_url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
    installer_path = os.path.join(venv_path, PYTHON_INSTALLER)
    
    print(f"[{GREEN} -- {RESET}] Downloading Python {PYTHON_VERSION} installer...")
    run_command(f"curl -o {installer_path} {python_installer_url}")

    print(f"[{GREEN} -- {RESET}] Installing Python {PYTHON_VERSION} in the virtual environment...")
    run_command(f"{installer_path} /quiet InstallAllUsers=0 TargetDir={venv_path}")
    print(f"[{GREEN} OK {RESET}] Python {PYTHON_VERSION} installed in the virtual environment.")

def run_main_script(venv_path):
    python_path = venv_path / "Scripts" / "python" if os.name == "nt" else venv_path / "bin" / "python"
    print(f"[{GREEN} -- {RESET}] Running {SCRIPT_PATH}...")
    logging.info(f"Running {SCRIPT_PATH}...")
    run_command(f"{python_path} {SCRIPT_PATH}")

def main():
    venv_path = Path(VENV_NAME)
    requirements_path = Path(REQUIREMENTS_FILE)

    # Check if requirements file exists
    if not requirements_path.exists():
        print(f"[{RED} FAILED {RESET}] Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
        logging.error(f"Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
        sys.exit(1)

    # Check if virtual environment exists and is valid
    if venv_exists(venv_path):
        print(f"[{GREEN} -- {RESET}] Virtual environment exists. Checking Python version and dependencies...")
        logging.info("Virtual environment exists. Checking Python version and dependencies...")

        if check_python_version(venv_path) and dependencies_installed(venv_path):
            print(f"[{GREEN} OK {RESET}] The virtual environment is valid, with the correct Python version and dependencies.")
            logging.info("The virtual environment is valid, with the correct Python version and dependencies.")
        else:
            print(f"[{RED} -- {RESET}] Python version or dependencies are missing or outdated. Reinstalling...")
            logging.warning("Python version or dependencies are missing or outdated. Reinstalling...")
            install_requirements(venv_path)

    else:
        print(f"[{RED} FAILED {RESET}] Virtual environment does not exist or is invalid.")
        logging.error("Virtual environment does not exist or is invalid.")
        create_new_venv(venv_path)
        install_requirements(venv_path)

    # Ensure Python version is installed in the virtual environment
    if not check_python_version(venv_path):
        install_python_in_venv(venv_path)

    # Run the main script
    try:
        run_main_script(venv_path)

    except Exception as err:
        print("Error executing script. Check logs for more details")
        logging.error(f"Error while executing script: {err}")

if __name__ == "__main__":
    setup_logging()
    main()
