#!/usr/bin/env python3
"""
orphan_notes.py: Find and report on notes without connections.

This script identifies notes that lack backlinks or tags, helping maintain
a well-connected knowledge base.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuration
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"

class Note:
    """Represents a note with its metadata and connections."""
    def __init__(self, path: str):
        self.path = path
        self.links: Set[str] = set()
        self.backlinks: Set[str] = set()
        self.tags: Set[str] = set()
        self.has_metadata = False
        self._parse()
    
    def _parse(self) -> None:
        """Parse the note to extract links, tags, and metadata."""
        try:
            with open(self.path, 'r') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if content.startswith('---'):
                self.has_metadata = True
                _, fm, content = content.split('---', 2)
                try:
                    metadata = yaml.safe_load(fm)
                    if metadata and 'tags' in metadata:
                        self.tags.update(metadata['tags'])
                except Exception:
                    pass
            
            # Find wiki-style links
            self.links.update(
                re.findall(r'\[\[(.*?)\]\]', content)
            )
            
            # Find hashtag-style tags
            self.tags.update(
                tag[1:] for tag in re.findall(r'#(\w+)', content)
            )
        
        except Exception as e:
            print(f"Error parsing {self.path}: {e}")

def find_notes() -> Dict[str, Note]:
    """Find and parse all notes in the system."""
    notes = {}
    
    for directory in [NOTES_DIR, PROJECTS_DIR]:
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                notes[file_path] = Note(file_path)
    
    return notes

def build_backlinks(notes: Dict[str, Note]) -> None:
    """Build backlink relationships between notes."""
    # Create a mapping of note names to paths
    name_to_path = {}
    for path in notes:
        name = os.path.basename(path)
        name_to_path[name] = path
        name_without_ext = os.path.splitext(name)[0]
        name_to_path[name_without_ext] = path
    
    # Build backlinks
    for path, note in notes.items():
        for link in note.links:
            # Try to find the linked note
            linked_path = name_to_path.get(link)
            if linked_path and linked_path in notes:
                notes[linked_path].backlinks.add(path)

def find_orphans(notes: Dict[str, Note]) -> Dict[str, List[str]]:
    """Find notes that are disconnected from the network."""
    orphans = {
        'no_links': [],      # No outgoing links
        'no_backlinks': [],  # No incoming links
        'no_tags': [],       # No tags
        'no_metadata': [],   # No YAML frontmatter
        'isolated': []       # No connections at all
    }
    
    for path, note in notes.items():
        is_orphaned = True
        
        if not note.links:
            orphans['no_links'].append(path)
        else:
            is_orphaned = False
        
        if not note.backlinks:
            orphans['no_backlinks'].append(path)
        else:
            is_orphaned = False
        
        if not note.tags:
            orphans['no_tags'].append(path)
        else:
            is_orphaned = False
        
        if not note.has_metadata:
            orphans['no_metadata'].append(path)
        
        if is_orphaned:
            orphans['isolated'].append(path)
    
    return orphans

def suggest_connections(
    note_path: str,
    notes: Dict[str, Note]
) -> List[Tuple[str, float]]:
    """Suggest potential connections for an orphaned note."""
    target_note = notes[note_path]
    suggestions = []
    
    # Get the note's content
    with open(note_path, 'r') as f:
        content = f.read().lower()
    
    # Compare with other notes
    for other_path, other_note in notes.items():
        if other_path == note_path:
            continue
        
        # Simple text similarity check
        with open(other_path, 'r') as f:
            other_content = f.read().lower()
        
        # Count word overlap
        words = set(re.findall(r'\w+', content))
        other_words = set(re.findall(r'\w+', other_content))
        overlap = len(words & other_words)
        
        if overlap > 10:  # Arbitrary threshold
            similarity = overlap / len(words | other_words)
            suggestions.append((other_path, similarity))
    
    return sorted(suggestions, key=lambda x: x[1], reverse=True)[:5]

def generate_report(
    orphans: Dict[str, List[str]],
    notes: Dict[str, Note]
) -> str:
    """Generate a detailed report of orphaned notes."""
    report = ["# Orphaned Notes Report\n"]
    
    # Summary
    report.extend([
        "## Summary\n",
        f"- Notes without outgoing links: {len(orphans['no_links'])}",
        f"- Notes without incoming links: {len(orphans['no_backlinks'])}",
        f"- Notes without tags: {len(orphans['no_tags'])}",
        f"- Notes without metadata: {len(orphans['no_metadata'])}",
        f"- Completely isolated notes: {len(orphans['isolated'])}\n"
    ])
    
    # Detailed sections
    if orphans['isolated']:
        report.extend([
            "## Completely Isolated Notes\n",
            "These notes have no connections at all:\n"
        ])
        for path in orphans['isolated']:
            relative_path = os.path.relpath(path, "..")
            report.append(f"\n### `{relative_path}`")
            
            # Add suggestions
            suggestions = suggest_connections(path, notes)
            if suggestions:
                report.append("\nSuggested connections:")
                for suggested_path, similarity in suggestions:
                    rel_path = os.path.relpath(suggested_path, "..")
                    report.append(
                        f"- `{rel_path}` "
                        f"(similarity: {similarity:.2%})"
                    )
    
    # Other categories
    categories = {
        'no_links': "Notes Without Outgoing Links",
        'no_backlinks': "Notes Without Incoming Links",
        'no_tags': "Notes Without Tags",
        'no_metadata': "Notes Without Metadata"
    }
    
    for key, title in categories.items():
        if orphans[key] and key != 'isolated':
            report.extend([f"\n## {title}\n"])
            for path in orphans[key]:
                relative_path = os.path.relpath(path, "..")
                report.append(f"- `{relative_path}`")
    
    # Add recommendations
    report.extend([
        "\n## Recommendations\n",
        "1. Add YAML frontmatter to notes missing metadata",
        "2. Tag notes based on their content and themes",
        "3. Add wiki-style links to connect related notes",
        "4. Review completely isolated notes for relevance"
    ])
    
    return '\n'.join(report)

def main() -> None:
    """Main function to find and report on orphaned notes."""
    print("Analyzing note connections...")
    
    # Find and analyze notes
    notes = find_notes()
    build_backlinks(notes)
    orphans = find_orphans(notes)
    
    # Generate and save report
    report = generate_report(orphans, notes)
    report_path = os.path.join(NOTES_DIR, "meta", "orphan-notes-report.md")
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nFound {len(orphans['isolated'])} completely isolated notes")
    print(f"Full report saved to: {report_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error analyzing notes: {e}")
