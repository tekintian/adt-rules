#!/usr/bin/env python3
"""
Pre-commit script to update MD5 hashes for all .txt and .conf files in the project.
This script automatically:
1. Updates Version: lines in all .txt and .conf files (excluding adbyby directory handled separately)
2. Calculates MD5 hashes for all .txt and .conf files in the project
3. Updates the root md5.json file with the results
4. Stages all updated files for commit
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

def is_file_content_modified(filepath, exclude_version_line=True):
    """Check if file content is actually modified (excluding version line if specified)."""
    def has_non_version_changes(diff_content):
        """Check if diff contains non-version line changes."""
        if exclude_version_line:
            # Filter out version line changes from diff
            lines = diff_content.split('\n')
            # Check if there are changes that are NOT version lines
            for line in lines:
                if line.startswith(('+', '-')) and not line.startswith(('---', '+++')):
                    # Skip version lines
                    if any(pattern in line for pattern in ['Version:', 'version:', 'VERSION:']):
                        continue
                    # Found a non-version change
                    return True
            return False
        else:
            return bool(diff_content.strip())
    
    try:
        # Check if file has unstaged changes
        result = subprocess.run(['git', 'diff', str(filepath)], 
                              capture_output=True, text=True, check=False)
        
        if result.stdout.strip():  # Check if there's any diff output
            if has_non_version_changes(result.stdout):
                return True
        
        # Check if file has staged changes
        result = subprocess.run(['git', 'diff', '--cached', str(filepath)], 
                              capture_output=True, text=True, check=False)
        
        if result.stdout.strip():  # Check if there's any diff output
            if has_non_version_changes(result.stdout):
                return True
        
        # Check if file is untracked
        result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', str(filepath)], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            return True
        
        return False
    except Exception as e:
        print(f"Error checking git status for {filepath}: {e}")
        # If we can't check git status, assume file is modified to be safe
        return True

def update_version_in_file(filepath):
    """Update Version line in any file with current timestamp only if file is modified."""
    # Check if file is actually modified in git (excluding version line changes)
    if not is_file_content_modified(filepath, exclude_version_line=True):
        print(f"Skipping {filepath.name}: no content changes detected")
        return False
    
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"No content in {filepath.name}")
            return False
        
        # Check first line for version pattern: ! Version: or # Version:
        first_line = lines[0].strip()
        
        # Pattern for first line version: ! Version: ... or # Version: ...
        version_patterns = [
            (r'^! Version: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '! Version:'),
            (r'^# Version: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '# Version:'),
            (r'^! Version: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '! Version:'),
            (r'^# Version: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '# Version:')
        ]
        
        updated = False
        for pattern, prefix in version_patterns:
            if re.match(pattern, first_line):
                # Determine format (T or space) based on original
                if 'T' in first_line:
                    timestamp = current_time
                else:
                    timestamp = current_time.replace("T", " ")
                
                # Update first line
                lines[0] = f'{prefix} {timestamp}\n'
                updated = True
                print(f"Updated version in {filepath.name}: {prefix} {timestamp}")
                break
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        else:
            print(f"No version line found in first line of {filepath.name}")
            return False
            
    except Exception as e:
        print(f"Error updating version in {filepath}: {e}")
        return False

def update_md5_json():
    """Update md5.json with current file hashes for the entire project."""
    project_root = Path(".")
    md5_file = project_root / "md5.json"
    
    # Files that need version updates in adbyby directory
    adbyby_dir = project_root / "adbyby"
    # adbyby_version_files = ['video.txt', 'lazy.txt']
    files_to_stage = []
    
    # Find all .txt and .conf files in the project
    txt_conf_files = []
    for pattern in ['*.txt', '*.conf']:
        for file_path in project_root.rglob(pattern):
            # Skip adbyby directory files (already handled) and md5.json
            if file_path.name == 'md5.json':
                continue
            txt_conf_files.append(file_path)
    
    # Update version information in other files
    for file_path in txt_conf_files:
        if update_version_in_file(file_path):
            files_to_stage.append(str(file_path))
    
    # Collect all files for MD5 calculation (all .txt and .conf files including adbyby)
    all_files = []
    for pattern in ['*.txt', '*.conf']:
        for file_path in project_root.rglob(pattern):
            # Skip md5.json itself
            if file_path.name == 'md5.json':
                continue
            all_files.append(file_path)
    
    # Calculate MD5 for all files
    md5_data = {}
    adbyby_md5_data = {}
    
    for file_path in all_files:
        try:
            # Use relative path from project root as key, but without extension for consistency
            relative_path = file_path.relative_to(project_root)
            key = str(relative_path) # Use relative path as key, but without extension for consistency
            md5_value = calculate_md5(file_path)
            md5_data[key] = md5_value
            # If file is in adbyby directory, store in adbyby_md5_data
            if 'adbyby/' in str(file_path):
                # adbyby files use relative path without extension
                adbyby_md5_data[relative_path.name] = md5_value
            
            print(f"Updated {key}: {md5_value}")
        except Exception as e:
            print(f"Error calculating MD5 for {file_path}: {e}")
    
    # Write updated JSON to root directory
    with open(md5_file, 'w', encoding='utf-8') as f:
        # Sort keys for consistent ordering
        sorted_keys = sorted(md5_data.keys())
        md5_data = {k: md5_data[k] for k in sorted_keys}
        
        json.dump(md5_data, f, separators=(',', ':'), ensure_ascii=False, indent=2)
    
    # Write updated adbyby JSON to adbyby directory
    adbyby_md5_file = adbyby_dir / "md5.json"
    with open(adbyby_md5_file, 'w', encoding='utf-8') as f:
        # Sort keys for consistent ordering
        sorted_keys = sorted(adbyby_md5_data.keys())
        adbyby_md5_data = {k: adbyby_md5_data[k] for k in sorted_keys}
        
        json.dump(adbyby_md5_data, f, separators=(',', ':'), ensure_ascii=False, indent=2)
    
    # Stage md5.json and adbyby/md5.json files
    files_to_stage.append(str(adbyby_md5_file))
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