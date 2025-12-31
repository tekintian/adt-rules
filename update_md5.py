#!/usr/bin/env python3
"""
Pre-commit script to update Version and Checksum for all .txt and .conf files in the project.
This script automatically:
1. Updates ! Version: and ! Checksum: lines in .txt files
2. Updates # Version: and # Checksum: lines in .conf files
3. Calculates MD5 hashes for all .txt and .conf files in the project
4. Updates the root md5.json file with the results
5. Updates adbyby/md5.json for files in the adbyby directory
6. Stages all updated files for commit
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

def is_file_content_modified(filepath, exclude_version_line=True, exclude_checksum_line=True):
    """Check if file content is actually modified (excluding version/checksum lines if specified)."""
    def has_non_metadata_changes(diff_content):
        """Check if diff contains non-version/non-checksum line changes."""
        patterns_to_exclude = []
        if exclude_version_line:
            patterns_to_exclude.extend(['Version:', 'version:', 'VERSION:'])
        if exclude_checksum_line:
            patterns_to_exclude.extend(['Checksum:', 'checksum:', 'CHECKSUM:'])
        
        if patterns_to_exclude:
            # Filter out version/checksum line changes from diff
            lines = diff_content.split('\n')
            # Check if there are changes that are NOT version/checksum lines
            for line in lines:
                if line.startswith(('+', '-')) and not line.startswith(('---', '+++')):
                    # Skip version and checksum lines
                    if any(pattern in line for pattern in patterns_to_exclude):
                        continue
                    # Found a non-version/non-checksum change
                    return True
            return False
        else:
            return bool(diff_content.strip())
    
    try:
        # Check if file has unstaged changes
        result = subprocess.run(['git', 'diff', str(filepath)], 
                              capture_output=True, text=True, check=False)
        
        if result.stdout.strip():  # Check if there's any diff output
            if has_non_metadata_changes(result.stdout):
                return True
        
        # Check if file has staged changes
        result = subprocess.run(['git', 'diff', '--cached', str(filepath)], 
                              capture_output=True, text=True, check=False)
        
        if result.stdout.strip():  # Check if there's any diff output
            if has_non_metadata_changes(result.stdout):
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

def update_version_and_checksum_in_file(filepath):
    """Update Version and Checksum lines in a file only if file is modified."""
    # Check if file is actually modified in git (excluding version/checksum lines)
    if not is_file_content_modified(filepath, exclude_version_line=True, exclude_checksum_line=True):
        return False
    
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return False
        
        updated = False
        version_updated = False
        checksum_updated = False
        
        # Process each line to find and update Version and Checksum
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Update Version line
            if not version_updated:
                version_patterns = [
                    (r'^! Version: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '! Version:'),
                    (r'^# Version: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '# Version:'),
                    (r'^! Version: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '! Version:'),
                    (r'^# Version: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '# Version:')
                ]
                
                for pattern, prefix in version_patterns:
                    if re.match(pattern, stripped):
                        # Determine format (T or space) based on original
                        if 'T' in stripped:
                            timestamp = current_time
                        else:
                            timestamp = current_time.replace("T", " ")
                        
                        # Update version line
                        lines[i] = f'{prefix} {timestamp}\n'
                        version_updated = True
                        updated = True
                        print(f"Updated version in {filepath.name}: {prefix} {timestamp}")
                        break
            
            # Update Checksum line
            if not checksum_updated:
                checksum_patterns = [
                    r'^! Checksum: [a-fA-F0-9]{32}',
                    r'^# Checksum: [a-fA-F0-9]{32}'
                ]
                
                for pattern in checksum_patterns:
                    if re.match(pattern, stripped):
                        # Mark that we found a checksum line
                        checksum_line_index = i
                        checksum_prefix = stripped.split('Checksum:')[0].strip()
                        checksum_updated = True
                        updated = True
                        break
        
        # After all metadata updates, calculate the final checksum
        if checksum_updated:
            final_content = ''.join(lines)
            final_checksum = hashlib.md5(final_content.encode('utf-8')).hexdigest()
            
            # Find and update checksum line
            for i, line in enumerate(lines):
                if 'Checksum:' in line:
                    # Determine the prefix based on original line
                    if line.strip().startswith('!'):
                        prefix = '!'
                    elif line.strip().startswith('#'):
                        prefix = '#'
                    else:
                        prefix = ''
                    lines[i] = f'{prefix} Checksum: {final_checksum}\n'
                    print(f"Updated checksum in {filepath.name}: {final_checksum}")
                    break
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error updating version/checksum in {filepath}: {e}")
        return False

def update_md5_json():
    """Update md5.json with current file hashes for the entire project."""
    project_root = Path(".")
    md5_file = project_root / "md5.json"
    adbyby_dir = project_root / "adbyby"
    adbyby_md5_file = adbyby_dir / "md5.json"
    
    files_to_stage = []
    
    # Find all .txt and .conf files in the project
    txt_conf_files = []
    for pattern in ['*.txt', '*.conf']:
        for file_path in project_root.rglob(pattern):
            # Skip md5.json files
            if file_path.name == 'md5.json':
                continue
            txt_conf_files.append(file_path)
    
    # Update version and checksum information in all files
    for file_path in txt_conf_files:
        if update_version_and_checksum_in_file(file_path):
            files_to_stage.append(str(file_path))
    
    # Collect all files for MD5 calculation (all .txt and .conf files)
    all_files = []
    for pattern in ['*.txt', '*.conf']:
        for file_path in project_root.rglob(pattern):
            # Skip md5.json files
            if file_path.name == 'md5.json':
                continue
            all_files.append(file_path)
    
    # Calculate MD5 for all files
    md5_data = {}
    adbyby_md5_data = {}
    
    for file_path in all_files:
        try:
            relative_path = file_path.relative_to(project_root)
            md5_value = calculate_md5(file_path)
            
            # Root md5.json uses relative path as key
            md5_data[str(relative_path)] = md5_value
            
            # adbyby md5.json uses filename without extension as key
            if 'adbyby/' in str(relative_path):
                adbyby_md5_data[relative_path.stem] = md5_value
            
        except Exception as e:
            print(f"Error calculating MD5 for {file_path}: {e}")
    
    # Write updated JSON to root directory
    with open(md5_file, 'w', encoding='utf-8') as f:
        # Sort keys for consistent ordering
        sorted_keys = sorted(md5_data.keys())
        md5_data = {k: md5_data[k] for k in sorted_keys}
        json.dump(md5_data, f, separators=(',', ':'), ensure_ascii=False, indent=2)
    
    # Write updated adbyby JSON to adbyby directory
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