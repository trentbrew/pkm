#!/usr/bin/env python3
"""
project_cleaner.py: Manage and archive inactive projects.

This script identifies inactive projects and moves them to the archive,
maintaining a clean and focused project space.
"""

import os
import shutil
import yaml
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
PROJECTS_DIR = "../03-Projects"
ARCHIVE_DIR = "../05-Archive/projects"
ARCHIVE_LOG = os.path.join("../05-Archive", "log.md")
INACTIVE_THRESHOLD_DAYS = 90  # 3 months

def get_project_status(project_dir: str) -> Tuple[datetime.datetime, str]:
    """Get the last modification time and status of a project."""
    last_modified = datetime.datetime.fromtimestamp(0)
    status = "unknown"
    
    # Check all files in the project
    for root, _, files in os.walk(project_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            mod_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            
            if mod_time > last_modified:
                last_modified = mod_time
            
            # Try to determine status from metadata
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if content.startswith('---'):
                    _, fm, _ = content.split('---', 2)
                    metadata = yaml.safe_load(fm)
                    if metadata and 'status' in metadata:
                        status = metadata['status']
            except Exception:
                pass
    
    return last_modified, status

def find_inactive_projects() -> List[Tuple[str, datetime.datetime, str]]:
    """Find projects that haven't been modified recently."""
    inactive_projects = []
    cutoff = datetime.datetime.now() - datetime.timedelta(
        days=INACTIVE_THRESHOLD_DAYS
    )
    
    for item in os.listdir(PROJECTS_DIR):
        project_dir = os.path.join(PROJECTS_DIR, item)
        if not os.path.isdir(project_dir):
            continue
        
        last_modified, status = get_project_status(project_dir)
        
        if (last_modified < cutoff and status != "active") or status == "completed":
            inactive_projects.append((project_dir, last_modified, status))
    
    return inactive_projects

def update_project_metadata(project_dir: str) -> None:
    """Update metadata in project files to reflect archived status."""
    for root, _, files in os.walk(project_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    _, fm, body = content.split('---', 2)
                    metadata = yaml.safe_load(fm) or {}
                    
                    # Update metadata
                    metadata['status'] = 'archived'
                    metadata['archived_date'] = datetime.datetime.now().strftime(
                        '%Y-%m-%d'
                    )
                    
                    # Write updated content
                    with open(file_path, 'w') as f:
                        f.write('---\n')
                        yaml.dump(metadata, f)
                        f.write('---\n')
                        f.write(body)
            
            except Exception as e:
                print(f"Error updating metadata for {file_path}: {e}")

def log_archived_project(
    project_dir: str,
    last_modified: datetime.datetime,
    status: str
) -> None:
    """Log archived project details."""
    project_name = os.path.basename(project_dir)
    archive_entry = (
        f"\n## Archived Project: {project_name}\n"
        f"- Archived on: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
        f"- Last modified: {last_modified.strftime('%Y-%m-%d')}\n"
        f"- Previous status: {status}\n"
        f"- Original location: `{os.path.relpath(project_dir, '..')}`\n"
    )
    
    # Create or append to archive log
    os.makedirs(os.path.dirname(ARCHIVE_LOG), exist_ok=True)
    if not os.path.exists(ARCHIVE_LOG):
        with open(ARCHIVE_LOG, 'w') as f:
            f.write("# Archive Log\n\nLog of archived items.\n")
    
    with open(ARCHIVE_LOG, 'a') as f:
        f.write(archive_entry)

def archive_project(
    project_dir: str,
    last_modified: datetime.datetime,
    status: str
) -> None:
    """Archive a single project."""
    project_name = os.path.basename(project_dir)
    archive_path = os.path.join(ARCHIVE_DIR, project_name)
    
    # Create archive directory
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Update metadata before moving
    update_project_metadata(project_dir)
    
    # Move project to archive
    shutil.move(project_dir, archive_path)
    
    # Log the archival
    log_archived_project(project_dir, last_modified, status)

def generate_summary(archived_projects: List[Tuple[str, datetime.datetime, str]]) -> str:
    """Generate a summary of archived projects."""
    summary = [
        "# Project Archival Summary\n",
        f"Archived on: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    ]
    
    if archived_projects:
        summary.append("## Archived Projects:\n")
        for project_dir, last_modified, status in archived_projects:
            project_name = os.path.basename(project_dir)
            summary.extend([
                f"### {project_name}",
                f"- Last modified: {last_modified.strftime('%Y-%m-%d')}",
                f"- Previous status: {status}",
                f"- New location: `/05-Archive/projects/{project_name}`\n"
            ])
    else:
        summary.append("No projects were archived.\n")
    
    return '\n'.join(summary)

def main() -> None:
    """Main function to clean up inactive projects."""
    print("Checking for inactive projects...")
    
    # Find inactive projects
    inactive_projects = find_inactive_projects()
    
    if not inactive_projects:
        print("No inactive projects found.")
        return
    
    print(f"\nFound {len(inactive_projects)} inactive projects:")
    for project_dir, last_modified, status in inactive_projects:
        print(
            f"- {os.path.basename(project_dir)} "
            f"(last modified: {last_modified.strftime('%Y-%m-%d')}, "
            f"status: {status})"
        )
    
    # Archive projects
    for project_dir, last_modified, status in inactive_projects:
        try:
            archive_project(project_dir, last_modified, status)
            print(f"\nArchived: {os.path.basename(project_dir)}")
        except Exception as e:
            print(f"Error archiving {project_dir}: {e}")
    
    # Generate and save summary
    summary = generate_summary(inactive_projects)
    summary_path = os.path.join(ARCHIVE_DIR, "archive-summary.md")
    
    with open(summary_path, 'w') as f:
        f.write(summary)
    
    print(f"\nArchival complete. Summary saved to: {summary_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error cleaning projects: {e}")
