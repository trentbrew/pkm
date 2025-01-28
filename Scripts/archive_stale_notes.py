#!/usr/bin/env python3
"""
archive_stale_notes.py: Identify and archive stale notes and projects.

This script scans the Notes and Projects directories for files that haven't been
modified in a specified timeframe and moves them to the Archive directory.
"""

import os
import shutil
import datetime
import yaml
from pathlib import Path
from typing import List, Tuple

# Configuration
STALE_THRESHOLD_DAYS = 180  # 6 months
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
ARCHIVE_DIR = "../05-Archive"
ARCHIVE_LOG = os.path.join(ARCHIVE_DIR, "log.md")

def get_stale_files(directory: str, days: int) -> List[Tuple[str, datetime.datetime]]:
    """Find files that haven't been modified in the specified number of days."""
    stale_files = []
    now = datetime.datetime.now()
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            modified_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            
            if (now - modified_time).days > days:
                stale_files.append((file_path, modified_time))
    
    return stale_files

def update_file_metadata(file_path: str) -> None:
    """Add archived tag to file's YAML frontmatter."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file has YAML frontmatter
    if content.startswith('---'):
        try:
            # Split content into frontmatter and body
            _, fm, body = content.split('---', 2)
            metadata = yaml.safe_load(fm)
            
            # Add archived tag if not present
            if 'tags' in metadata:
                if 'archived' not in metadata['tags']:
                    metadata['tags'].append('archived')
            else:
                metadata['tags'] = ['archived']
                
            # Update archive date
            metadata['archived_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Write updated content
            with open(file_path, 'w') as f:
                f.write('---\n')
                yaml.dump(metadata, f)
                f.write('---\n')
                f.write(body)
        except Exception as e:
            print(f"Error updating metadata for {file_path}: {e}")

def log_archived_file(file_path: str, modified_time: datetime.datetime) -> None:
    """Log archived file details to the archive log."""
    archive_entry = (
        f"\n## Archived on {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
        f"- File: `{file_path}`\n"
        f"- Last modified: {modified_time.strftime('%Y-%m-%d')}\n"
        f"- Reason: No updates for {STALE_THRESHOLD_DAYS} days\n"
    )
    
    with open(ARCHIVE_LOG, 'a') as f:
        f.write(archive_entry)

def archive_stale_files() -> None:
    """Main function to archive stale files."""
    # Ensure archive directory exists
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Initialize archive log if it doesn't exist
    if not os.path.exists(ARCHIVE_LOG):
        with open(ARCHIVE_LOG, 'w') as f:
            f.write("# Archive Log\n\nLog of files moved to archive.\n")
    
    # Process notes
    stale_notes = get_stale_files(NOTES_DIR, STALE_THRESHOLD_DAYS)
    print(f"\nFound {len(stale_notes)} stale notes:")
    for file_path, modified_time in stale_notes:
        print(f"- {file_path} (last modified: {modified_time.strftime('%Y-%m-%d')})")
        
        # Create archive directory structure
        relative_path = os.path.relpath(file_path, NOTES_DIR)
        archive_path = os.path.join(ARCHIVE_DIR, 'notes', relative_path)
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        # Update metadata and move file
        update_file_metadata(file_path)
        shutil.move(file_path, archive_path)
        log_archived_file(file_path, modified_time)
    
    # Process projects
    stale_projects = get_stale_files(PROJECTS_DIR, STALE_THRESHOLD_DAYS)
    print(f"\nFound {len(stale_projects)} stale projects:")
    for file_path, modified_time in stale_projects:
        print(f"- {file_path} (last modified: {modified_time.strftime('%Y-%m-%d')})")
        
        # Create archive directory structure
        relative_path = os.path.relpath(file_path, PROJECTS_DIR)
        archive_path = os.path.join(ARCHIVE_DIR, 'projects', relative_path)
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        # Update metadata and move file
        update_file_metadata(file_path)
        shutil.move(file_path, archive_path)
        log_archived_file(file_path, modified_time)

if __name__ == "__main__":
    try:
        archive_stale_files()
        print("\nArchiving complete. Check archive log for details.")
    except Exception as e:
        print(f"Error during archiving: {e}")
