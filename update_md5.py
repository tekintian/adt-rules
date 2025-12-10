#!/usr/bin/env python3
"""
Pre-commit script to update MD5 hashes for adbyby files.
This script automatically calculates MD5 hashes for all files in the adbyby directory
(excluding md5.json) and updates the md5.json file with the results.
"""

import os
import json
import hashlib
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

def calculate_md5(filepath):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def update_version_in_file(filepath):
    """Update Version line in file with current timestamp."""
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Different patterns for different files
        if filepath.name == 'dnsmasq.adblock':
            # Pattern for dnsmasq.adblock: # Version: YYYY-MM-DD HH:MM:SS
            pattern = r'^# Version: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            replacement = f'# Version: {current_time.replace("T", " ")}'
        else:
            # Pattern for video.txt and lazy.txt: ! Version: YYYY-MM-DDTHH:MM:SS
            pattern = r'^! Version: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
            replacement = f'! Version: {current_time}'
        
        # Update the version line
        updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if updated_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated version in {filepath.name}: {replacement}")
            return True
        else:
            print(f"No version update needed for {filepath.name}")
            return False
            
    except Exception as e:
        print(f"Error updating version in {filepath}: {e}")
        return False

def update_md5_json():
    """Update md5.json with current file hashes."""
    adbyby_dir = Path("adbyby")
    md5_file = adbyby_dir / "md5.json"
    
    if not adbyby_dir.exists():
        print("adbyby directory not found, skipping MD5 update")
        return 0

    # Files that need version updates before MD5 calculation
    version_files = ['lazy.txt', 'video.txt', 'dnsmasq.adblock']
    handle_files =  version_files+ ['update3.js']
    files_to_stage = []
    
    # Update version information first
    for filename in version_files:
        file_path = adbyby_dir / filename
        if file_path.exists():
            if update_version_in_file(file_path):
                files_to_stage.append(str(file_path))
    
    # Collect file data
    md5_data = {}
    
    for file_path in adbyby_dir.iterdir():
        # Skip directories and md5.json itself
        if file_path.is_dir() or file_path.name == "md5.json" or file_path.name not in handle_files:
            continue
            
        # Use filename without extension as key
        key = file_path.stem
        md5_value = calculate_md5(file_path)
        md5_data[key] = md5_value
        
        print(f"Updated {key}: {md5_value}")
    
    # Write updated JSON
    with open(md5_file, 'w', encoding='utf-8') as f:
        json.dump(md5_data, f, separators=(',', ':'), ensure_ascii=False)
    
    files_to_stage.append(str(md5_file))
    
    # Stage all updated files
    for file_to_stage in files_to_stage:
        try:
            subprocess.run(['git', 'add', file_to_stage], check=True, capture_output=True)
            print(f"Staged updated {file_to_stage}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not stage {file_to_stage}: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(update_md5_json())