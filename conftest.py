"""
Configuration file for pytest.
This file is automatically found and loaded by pytest.
"""
import os
import sys

# Add the project root directory to the path so we can import modules from src
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)