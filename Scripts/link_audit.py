#!/usr/bin/env python3
"""
link_audit.py: Verify and optimize links between notes.

This script checks for broken links and suggests new connections
between related notes.
"""

import os
import re
import yaml
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuration
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
MIN_SIMILARITY = 0.3  # Minimum similarity score for suggesting links

class Link:
    """Represents a link between notes."""
    def __init__(self, source: str, target: str, context: str):
        self.source = source
        self.target = target
        self.context = context.strip()

class Note:
    """Represents a note with its content and metadata."""
    def __init__(self, path: str):
        self.path = path
        self.content = ""
        self.links: List[Link] = []
        self.tags: Set[str] = set()
        self.title = ""
        self._parse()
    
    def _parse(self) -> None:
        """Parse the note to extract content, links, and metadata."""
        try:
            with open(self.path, 'r') as f:
                content = f.read()
            
            self.content = content
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                _, fm, content = content.split('---', 2)
                try:
                    metadata = yaml.safe_load(fm)
                    if metadata:
                        if 'title' in metadata:
                            self.title = metadata['title']
                        if 'tags' in metadata:
                            self.tags.update(metadata['tags'])
                except Exception:
                    pass
            
            # Extract wiki-style links with context
            for match in re.finditer(r'\[\[(.*?)\]\]', content):
                link_target = match.group(1)
                
                # Get surrounding context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]
                
                self.links.append(Link(self.path, link_target, context))
        
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

def check_links(notes: Dict[str, Note]) -> Dict[str, List[Link]]:
    """Check for broken links in all notes."""
    broken_links = defaultdict(list)
    
    # Create a mapping of note names to paths
    name_to_path = {}
    for path in notes:
        name = os.path.basename(path)
        name_to_path[name] = path
        name_without_ext = os.path.splitext(name)[0]
        name_to_path[name_without_ext] = path
    
    # Check each note's links
    for note in notes.values():
        for link in note.links:
            if link.target not in name_to_path:
                broken_links[note.path].append(link)
    
    return broken_links

def calculate_similarity(note1: Note, note2: Note) -> float:
    """Calculate similarity between two notes."""
    # Get words from content (excluding common words)
    def get_words(text: str) -> Set[str]:
        words = set(re.findall(r'\b\w+\b', text.lower()))
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}
        return words - common_words
    
    words1 = get_words(note1.content)
    words2 = get_words(note2.content)
    
    # Calculate Jaccard similarity
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    # Boost similarity if tags overlap
    tag_overlap = len(note1.tags & note2.tags)
    tag_boost = tag_overlap * 0.1  # 10% boost per shared tag
    
    return min(1.0, (intersection / union) + tag_boost)

def suggest_links(notes: Dict[str, Note]) -> Dict[str, List[Tuple[str, float]]]:
    """Suggest new links between notes based on content similarity."""
    suggestions = defaultdict(list)
    
    # Compare each pair of notes
    paths = list(notes.keys())
    for i, path1 in enumerate(paths):
        note1 = notes[path1]
        
        for path2 in paths[i+1:]:
            note2 = notes[path2]
            
            # Skip if already linked
            if any(link.target in path2 for link in note1.links):
                continue
            
            similarity = calculate_similarity(note1, note2)
            if similarity >= MIN_SIMILARITY:
                suggestions[path1].append((path2, similarity))
                suggestions[path2].append((path1, similarity))
    
    # Sort suggestions by similarity
    for path in suggestions:
        suggestions[path] = sorted(
            suggestions[path],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Keep top 5 suggestions
    
    return suggestions

def generate_report(
    broken_links: Dict[str, List[Link]],
    suggestions: Dict[str, List[Tuple[str, float]]]
) -> str:
    """Generate a detailed link audit report."""
    report = ["# Link Audit Report\n"]
    
    # Broken links section
    if broken_links:
        report.extend([
            "## Broken Links\n",
            "The following links are broken and need to be fixed:\n"
        ])
        for source, links in broken_links.items():
            relative_source = os.path.relpath(source, "..")
            report.append(f"\n### In `{relative_source}`:")
            for link in links:
                report.extend([
                    f"- Broken link to: `{link.target}`",
                    f"  Context: \"...{link.context}...\""
                ])
    
    # Link suggestions section
    if suggestions:
        report.extend([
            "\n## Suggested Links\n",
            "Consider adding these connections between related notes:\n"
        ])
        for source, targets in suggestions.items():
            if not targets:
                continue
                
            relative_source = os.path.relpath(source, "..")
            report.append(f"\n### For `{relative_source}`:")
            
            for target, similarity in targets:
                relative_target = os.path.relpath(target, "..")
                report.append(
                    f"- `{relative_target}` "
                    f"(similarity: {similarity:.2%})"
                )
    
    # Add recommendations
    report.extend([
        "\n## Recommendations\n",
        "1. Fix broken links to maintain system integrity",
        "2. Review suggested connections for relevant links",
        "3. Consider adding bidirectional links for strong connections",
        "4. Update link text to provide better context"
    ])
    
    return '\n'.join(report)

def main() -> None:
    """Main function to audit links."""
    print("Auditing note links...")
    
    # Find and analyze notes
    notes = find_notes()
    print(f"Found {len(notes)} notes")
    
    # Check for broken links
    broken_links = check_links(notes)
    print(f"Found {sum(len(links) for links in broken_links.values())} broken links")
    
    # Generate link suggestions
    print("Analyzing note relationships...")
    suggestions = suggest_links(notes)
    
    # Generate and save report
    report = generate_report(broken_links, suggestions)
    report_path = os.path.join(NOTES_DIR, "meta", "link-audit-report.md")
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nFull report saved to: {report_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during link audit: {e}")
