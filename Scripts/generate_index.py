#!/usr/bin/env python3
"""
generate_index.py: Dynamically update the /00-Index files.

This script scans the Cognet system for new files and tags, updating the index
files with current information about the system's structure and content.
"""

import os
import yaml
import datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuration
INDEX_DIR = "../00-Index"
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
RESOURCES_DIR = "../04-Resources"

def extract_yaml_frontmatter(file_path: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if content.startswith('---'):
            _, fm, _ = content.split('---', 2)
            return yaml.safe_load(fm) or {}
    except Exception:
        return {}
    
    return {}

def collect_tags() -> Dict[str, List[str]]:
    """Collect all tags and their associated files."""
    tags = defaultdict(list)
    
    # Scan directories for markdown files
    for directory in [NOTES_DIR, PROJECTS_DIR]:
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                file_path = os.path.join(root, file)
                metadata = extract_yaml_frontmatter(file_path)
                
                if 'tags' in metadata:
                    for tag in metadata['tags']:
                        tags[tag].append(file_path)
    
    return tags

def find_recent_updates(days: int = 7) -> List[Tuple[str, datetime.datetime]]:
    """Find files modified in the last N days."""
    recent_files = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    
    for directory in [NOTES_DIR, PROJECTS_DIR]:
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                file_path = os.path.join(root, file)
                modified_time = datetime.datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                )
                
                if modified_time > cutoff:
                    recent_files.append((file_path, modified_time))
    
    return sorted(recent_files, key=lambda x: x[1], reverse=True)

def update_tags_file(tags: Dict[str, List[str]]) -> None:
    """Update the tags.md file with current tag information."""
    tags_content = ["# Tag Reference\n\n"]
    
    # Group tags by category
    categories = {
        'project': [],
        'concept': [],
        'status': [],
        'other': []
    }
    
    for tag, files in sorted(tags.items()):
        if tag.startswith('project-'):
            categories['project'].append((tag, files))
        elif tag in ['active', 'archived', 'completed']:
            categories['status'].append((tag, files))
        elif tag.startswith('concept-'):
            categories['concept'].append((tag, files))
        else:
            categories['other'].append((tag, files))
    
    # Write categorized tags
    for category, category_tags in categories.items():
        if category_tags:
            tags_content.append(f"## {category.title()} Tags\n")
            for tag, files in category_tags:
                tags_content.append(f"- #{tag} ({len(files)} files)")
                for file in files[:3]:  # Show only first 3 files
                    relative_path = os.path.relpath(file, "..")
                    tags_content.append(f"  - `{relative_path}`")
            tags_content.append("\n")
    
    # Write to file
    with open(os.path.join(INDEX_DIR, "tags.md"), 'w') as f:
        f.write('\n'.join(tags_content))

def update_index_file(tags: Dict[str, List[str]], recent_files: List[Tuple[str, datetime.datetime]]) -> None:
    """Update the main index.md file."""
    index_content = [
        "# Cognet System Overview\n",
        "Last updated: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
    ]
    
    # Add quick navigation
    index_content.extend([
        "## Quick Navigation\n",
        "- [Daily Notes](/01-Daily)",
        "- [Knowledge Base](/02-Notes)",
        "- [Active Projects](/03-Projects)",
        "- [Resources](/04-Resources)",
        "- [Archive](/05-Archive)\n\n"
    ])
    
    # Add recent updates
    index_content.append("## Recent Updates\n")
    for file_path, modified_time in recent_files[:5]:
        relative_path = os.path.relpath(file_path, "..")
        index_content.append(
            f"- {modified_time.strftime('%Y-%m-%d')}: `{relative_path}`"
        )
    
    # Add popular tags
    index_content.extend([
        "\n## Popular Tags\n",
        "Tags with the most associated files:\n"
    ])
    
    popular_tags = sorted(
        tags.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:5]
    
    for tag, files in popular_tags:
        index_content.append(f"- #{tag} ({len(files)} files)")
    
    # Write to file
    with open(os.path.join(INDEX_DIR, "index.md"), 'w') as f:
        f.write('\n'.join(index_content))

def generate_related_file() -> None:
    """Generate the related.md file showing connections between notes."""
    related_content = [
        "# Related Notes and Themes\n",
        "Automatically generated connections between notes based on shared tags and links.\n\n"
    ]
    
    # TODO: Implement link analysis to find related notes
    # This would involve parsing markdown files for [[wiki-style]] links
    # and building a graph of connections
    
    # For now, just create a placeholder
    related_content.extend([
        "## Note Clusters\n",
        "*(This file will be updated with actual note relationships)*\n"
    ])
    
    # Write to file
    with open(os.path.join(INDEX_DIR, "related.md"), 'w') as f:
        f.write('\n'.join(related_content))

def main() -> None:
    """Main function to update all index files."""
    print("Updating index files...")
    
    # Collect information
    tags = collect_tags()
    recent_files = find_recent_updates()
    
    # Update files
    update_tags_file(tags)
    print("- Updated tags.md")
    
    update_index_file(tags, recent_files)
    print("- Updated index.md")
    
    generate_related_file()
    print("- Updated related.md")
    
    print("\nIndex generation complete!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during index generation: {e}")
