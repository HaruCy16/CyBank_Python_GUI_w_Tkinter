"""
CyBank CLI Launcher
This script ensures proper Python path configuration before running the CLI.

TO ENSURE LANG NA MAG RURUN NG MAAYOS ANG CLI SA IBANG COMPUTERS.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the main CLI
from cli.main import main

if __name__ == "__main__":
    main()
