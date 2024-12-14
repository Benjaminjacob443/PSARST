import os
import subprocess
subprocess.run("python -m pip install colorama", check=True, shell=True)
import sys
from pathlib import Path
import shutil
import datetime
import re
import logging
import platform
from colorama import init, Fore, Style
import urllib.request

# Initialize colorama
init()

# Color constants
RED = Fore.RED
GREEN = Fore.GREEN
RESET = Style.RESET_ALL

# Configuration Constants
VENV_NAME = "psarst_env"
REQUIREMENTS_FILE = 'psarst_requirements.txt'
SCRIPT_DIR = Path(__file__).parent
requirements_path = SCRIPT_DIR / REQUIREMENTS_FILE
SCRIPT_PATH = "PSARST.py"
PYTHON_VERSION = "3.11.1"
LOGS_DIR = "logs"
PYTHON_INSTALLER = "python-installer.exe"
LOCAL_PYTHON_DIR = "local_python"


# Logging Setup
def setup_logging():
    try:
        base_log_dir = os.path.join(LOGS_DIR, 'Error Logs')
        os.makedirs(base_log_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file_path = os.path.join(base_log_dir, f"PSARST_{timestamp}.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file_path)]
        )
        logging.info("Logging setup completed.")
    except Exception as e:
        print(f"[{RED}FAILED{RESET}] Could not set up logging: {e}")
        sys.exit(1)

# Command Runner
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[{RED}FAILED{RESET}] Error executing command: {command}\n{e}")
        logging.error(f"Error executing command: {command}\n{e}")
        sys.exit(1)

# Virtual Environment Validation
def venv_exists(venv_path):
    python_path = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return python_path.exists()

def check_python_version(venv_path):
    python_path = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    result = subprocess.run([python_path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        python_version = result.stdout.decode().strip().split()[1]
        return python_version == PYTHON_VERSION
    return False

# Dependencies Check
# def dependencies_installed(venv_path):
#     pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"
    
#     def clean_version(version_str):
#         # Remove any extra characters that might be part of the version
#         return re.sub(r'[^0-9.]', '', version_str.strip())

#     try:
#         with open(requirements_path, "r") as f:
#             requirements = f.readlines()

#         for req in requirements:
#             req = req.strip()
#             if req:  # Skip empty lines
#                 # Skip ta-lib dependency checking entirely
#                 if "TA_Lib" in req:
#                     continue  # Skip checking ta-lib and move to the next package

#                 # Check if the package is already installed
#                 result = subprocess.run(
#                     [pip_path, "show", req.split("==")[0]],  # Only check the package name
#                     stdout=subprocess.PIPE,
#                     stderr=subprocess.PIPE,
#                 )
#                 if result.returncode != 0:  # If package not found
#                     print(f"[{RED} MISSING {RESET}] {req} is not installed.")
#                     logging.error(f"{req} is not installed.")
#                     return False
#                 else:
#                     # Get the installed version from the 'pip show' output
#                     installed_version = subprocess.run(
#                         [pip_path, "show", req.split("==")[0]],
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.PIPE,
#                     )
#                     installed_version = installed_version.stdout.decode().strip().split('\n')[1].split(': ')[1]
#                     installed_version = clean_version(installed_version)  # Clean the version string
                    
#                     # Compare with required version if specified
#                     if "==" in req:
#                         required_version = req.split("==")[1]
#                         required_version = clean_version(required_version)  # Clean the required version string
                        
#                         if installed_version != required_version:
#                             print(f"[{RED} VERSION MISMATCH {RESET}] {req} installed version {installed_version} doesn't match required {required_version}.")
#                             logging.error(f"{req} installed version {installed_version} doesn't match required {required_version}.")
#                             return False
#                         else:
#                             print(f"[{GREEN} OK {RESET}] {req} is already installed and up-to-date.")
#                             logging.info(f"{req} is already installed and up-to-date.")
#                     else:
#                         print(f"[{GREEN} OK {RESET}] {req} is already installed (latest version).")
#                         logging.info(f"{req} is already installed (latest version).")
#         return True

#     except FileNotFoundError:
#         print(f"[{RED} FAILED {RESET}] Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
#         logging.error(f"Requirements file '{REQUIREMENTS_FILE}' not found. Exiting.")
#         sys.exit(1)

def dependencies_installed(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"

    # Function to clean up version string to avoid issues with non-numeric characters
    def clean_version(version_str):
        return re.sub(r'[^0-9.]', '', version_str.strip())

    # Explicitly resolve the path of the requirements file relative to the script's directory
    requirements_path = Path(__file__).parent / REQUIREMENTS_FILE

    try:
        # Check if the requirements file exists
        if not requirements_path.exists():
            raise FileNotFoundError(f"Requirements file '{requirements_path}' not found.")
        
        # Open the requirements file
        with open(requirements_path, "r") as f:
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

    except FileNotFoundError as e:
        print(f"[{RED} FAILED {RESET}] {e}")
        print(requirements_path)
        logging.error(e)
        sys.exit(1)

def install_requirements(venv_path):
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"
    print(f"[{GREEN} -- {RESET}] Installing dependencies from {REQUIREMENTS_FILE}...")
    logging.info(f"Installing dependencies from {REQUIREMENTS_FILE}...")
    run_command(f"{pip_path} install -r {REQUIREMENTS_FILE}")
    print(f"[{GREEN} OK {RESET}] All dependencies installed.")
    logging.info(f"All dependencies installed.")

# Virtual Environment Creation
def create_new_venv(venv_path):
    print(f"[{GREEN}--{RESET}] Creating a new virtual environment at {venv_path}...")
    logging.info(f"Creating a new virtual environment at {venv_path}...")
    run_command(f"python -m venv {venv_path}")
    print(f"[{GREEN}OK{RESET}] Virtual environment created.")
    logging.info("Virtual environment created.")

# Main Script Runner
def run_main_script(venv_path):
    python_path = venv_path / ("Scripts/python" if os.name == "nt" else "bin/python")
    print(f"[{GREEN}--{RESET}] Running {SCRIPT_PATH}...")
    logging.info(f"Running {SCRIPT_PATH}...")
    run_command(f"{python_path} {SCRIPT_PATH}")

# Python Version Installer (placeholder for simplicity)
def check_or_install_python():
    local_python_path = Path(LOCAL_PYTHON_DIR) / f"python-{PYTHON_VERSION}"
    python_exe = local_python_path / "python.exe" if os.name == "nt" else local_python_path / "bin" / "python"

    # Check if Python version is already installed locally
    if python_exe.exists():
        result = subprocess.run([python_exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and PYTHON_VERSION in result.stdout.decode():
            print(f"[{GREEN} OK {RESET}] Python {PYTHON_VERSION} is already installed locally.")
            logging.info(f"Python {PYTHON_VERSION} is already installed locally.")
            return python_exe

    # If not, download and install Python locally
    print(f"[{GREEN} -- {RESET}] Python {PYTHON_VERSION} is not found. Downloading and installing locally...")
    python_installer_url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe" if os.name == "nt" else f"https://www.python.org/ftp/python/{PYTHON_VERSION}/Python-{PYTHON_VERSION}.tgz"
    installer_path = Path(LOCAL_PYTHON_DIR) / PYTHON_INSTALLER
    os.makedirs(local_python_path, exist_ok=True)

    try:
        with urllib.request.urlopen(python_installer_url) as response, open(installer_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"[{GREEN} OK {RESET}] Python installer downloaded to {installer_path}.")
        logging.info(f"Python installer downloaded to {installer_path}.")
    except Exception as e:
        print(f"[{RED} FAILED {RESET}] Failed to download Python installer: {e}")
        logging.error(f"Failed to download Python installer: {e}")
        sys.exit(1)

    # Install Python locally
    if os.name == "nt":
        run_command(f"{installer_path} /quiet InstallAllUsers=0 TargetDir={local_python_path} SimpleInstall=1")
    else:
        run_command(f"tar -xvzf {installer_path} -C {local_python_path}")
        run_command(f"cd {local_python_path} && ./configure && make && make install")

    print(f"[{GREEN} OK {RESET}] Python {PYTHON_VERSION} installed locally.")
    logging.info(f"Python {PYTHON_VERSION} installed locally.")
    return python_exe

# Main Function
def main():
    setup_logging()
    venv_path = Path(VENV_NAME)

    # Ensure the requirements file exists
    if not requirements_path.exists():
        print(f"[{RED}FAILED{RESET}] Requirements file '{REQUIREMENTS_FILE}' not found.")
        logging.error(f"Requirements file '{REQUIREMENTS_FILE}' not found.")
        sys.exit(1)



    # Check Python version and create virtual environment
    python_exe = check_or_install_python()
    if not venv_exists(venv_path):
        print(f"[{RED}MISSING{RESET}] Virtual environment does not exist. Creating...")
        logging.info("Virtual environment does not exist. Creating a new one...")
        create_new_venv(venv_path)
        install_requirements(venv_path)
    else:
        print(f"[{GREEN}OK{RESET}] Virtual environment exists. Validating dependencies...")
        logging.info("Virtual environment exists. Validating dependencies...")
        if not dependencies_installed(venv_path):
            print(f"[{RED}MISSING{RESET}] Dependencies are missing or outdated. Installing...")
            logging.warning("Dependencies are missing or outdated. Installing...")
            install_requirements(venv_path)

    # Run the main script
    run_main_script(venv_path)

if __name__ == "__main__":
    main()
