#!/usr/bin/env python3
"""
chaos_extractor.py: Process and organize content from chaos-pit.md.

This script analyzes the chaos-pit.md file, extracts structured information,
and creates appropriate notes or tasks in the correct locations.
"""

import os
import re
import yaml
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
CHAOS_PIT = "../01-Daily/chaos-pit.md"
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"

class ChaosPitEntry:
    """Represents a single entry from the chaos pit."""
    def __init__(self, content: str, tags: List[str] = None):
        self.content = content.strip()
        self.tags = tags or []
        self.entry_type = self._determine_type()
    
    def _determine_type(self) -> str:
        """Determine the type of entry based on content and tags."""
        # Check for task markers
        if re.match(r'^[-*] \[ \]|\btodo\b|task:', self.content.lower()):
            return 'task'
        
        # Check for concept/idea markers
        if any(tag in self.tags for tag in ['concept', 'idea']):
            return 'concept'
        
        # Check for project-related content
        if any(tag.startswith('project-') for tag in self.tags):
            return 'project'
        
        # Default to note
        return 'note'

def parse_chaos_pit() -> List[ChaosPitEntry]:
    """Parse the chaos-pit.md file into structured entries."""
    entries = []
    current_entry = []
    current_tags = []
    
    try:
        with open(CHAOS_PIT, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#'):
                if current_entry:
                    entries.append(ChaosPitEntry(
                        '\n'.join(current_entry),
                        current_tags
                    ))
                    current_entry = []
                    current_tags = []
                continue
            
            # Extract tags
            tags = re.findall(r'#(\w+)', line)
            if tags:
                current_tags.extend(tags)
            
            # Add line to current entry
            current_entry.append(line)
        
        # Add final entry if exists
        if current_entry:
            entries.append(ChaosPitEntry(
                '\n'.join(current_entry),
                current_tags
            ))
    
    except FileNotFoundError:
        print(f"Error: {CHAOS_PIT} not found")
        return []
    
    return entries

def create_note(entry: ChaosPitEntry) -> str:
    """Create a new note from a chaos pit entry."""
    # Generate filename from first line of content
    first_line = entry.content.split('\n')[0]
    filename = re.sub(r'[^\w\s-]', '', first_line.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    
    if entry.entry_type == 'concept':
        filepath = os.path.join(NOTES_DIR, 'concepts', f"{filename}.md")
    else:
        filepath = os.path.join(NOTES_DIR, 'questions', f"{filename}.md")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Create note content with YAML frontmatter
    content = [
        "---",
        "title: " + first_line,
        "tags: [" + ", ".join(f'"{tag}"' for tag in entry.tags) + "]",
        "created: " + datetime.datetime.now().strftime('%Y-%m-%d'),
        "source: chaos-pit",
        "---",
        "",
        entry.content
    ]
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(content))
    
    return filepath

def add_to_project(entry: ChaosPitEntry) -> str:
    """Add entry to appropriate project file."""
    # Find project tag
    project_tag = next(
        (tag for tag in entry.tags if tag.startswith('project-')),
        'uncategorized'
    )
    
    project_name = project_tag.replace('project-', '')
    project_dir = os.path.join(PROJECTS_DIR, project_name)
    
    # Create project directory if it doesn't exist
    os.makedirs(project_dir, exist_ok=True)
    
    # Add to tasks.md in project directory
    tasks_file = os.path.join(project_dir, 'tasks.md')
    if not os.path.exists(tasks_file):
        with open(tasks_file, 'w') as f:
            f.write("# Project Tasks\n\n")
    
    with open(tasks_file, 'a') as f:
        f.write(f"\n## Added {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(entry.content + "\n")
    
    return tasks_file

def clean_chaos_pit() -> None:
    """Clean up the chaos pit after processing."""
    with open(CHAOS_PIT, 'w') as f:
        f.write("# Chaos Pit\n\n")
        f.write("Drop your raw thoughts, ideas, and quick captures here. ")
        f.write("Process these during your daily review.\n\n")
        f.write("## Unprocessed Items\n")
        f.write("- \n")

def main() -> None:
    """Main function to process chaos pit entries."""
    print("Processing chaos pit...")
    
    entries = parse_chaos_pit()
    processed_files = []
    
    for entry in entries:
        if entry.entry_type in ['concept', 'note']:
            filepath = create_note(entry)
            processed_files.append(('note', filepath))
        elif entry.entry_type in ['task', 'project']:
            filepath = add_to_project(entry)
            processed_files.append(('task', filepath))
    
    # Report results
    print("\nProcessed entries:")
    for entry_type, filepath in processed_files:
        relative_path = os.path.relpath(filepath, "..")
        print(f"- Created {entry_type}: {relative_path}")
    
    # Clean up chaos pit
    clean_chaos_pit()
    print("\nChaos pit cleaned and ready for new entries!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error processing chaos pit: {e}")
