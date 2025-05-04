#!/usr/bin/env python
"""
Startup Mentor - PG & Sam Altman-style startup advice
This is the main entry point for Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path

# Set environment variable to indicate we're running on Streamlit Cloud
os.environ['STREAMLIT_CLOUD'] = 'True'

# Add the src directory to the Python path
project_root = Path(__file__).resolve().parent
src_path = str(project_root / "src")
scripts_path = str(project_root / "scripts")

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Run the mentor UI
import scripts.mentor_ui 