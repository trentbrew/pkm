#!/usr/bin/env python3
"""
theme_clustering.py: Identify and analyze thematic clusters in notes.

This script analyzes note relationships to identify thematic clusters
and generates theme-specific index files.
"""

import os
import re
import yaml
import datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np

# Configuration
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
MIN_THEME_SIZE = 3  # Minimum notes in a theme
SIMILARITY_THRESHOLD = 0.3  # Minimum similarity for clustering

@dataclass
class Note:
    """Represents a note with its content and metadata."""
    path: str
    title: str
    content: str
    tags: Set[str]
    links: Set[str]
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Note':
        """Create a Note instance from a file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            title = os.path.splitext(os.path.basename(file_path))[0]
            tags = set()
            links = set()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                _, fm, content = content.split('---', 2)
                try:
                    metadata = yaml.safe_load(fm)
                    if metadata:
                        if 'title' in metadata:
                            title = metadata['title']
                        if 'tags' in metadata:
                            tags.update(metadata['tags'])
                except Exception:
                    pass
            
            # Extract wiki-style links
            links.update(re.findall(r'\[\[(.*?)\]\]', content))
            
            # Extract hashtag-style tags
            tags.update(tag[1:] for tag in re.findall(r'#(\w+)', content))
            
            return cls(file_path, title, content, tags, links)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

class ThemeCluster:
    """Represents a cluster of thematically related notes."""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.notes: List[Note] = []
        self.tags = Counter()
        self.common_links = set()
    
    def add_note(self, note: Note) -> None:
        """Add a note to the cluster and update metadata."""
        self.notes.append(note)
        for tag in note.tags:
            self.tags[tag] += 1
        if not self.common_links:
            self.common_links = set(note.links)
        else:
            self.common_links &= set(note.links)
    
    def get_summary(self) -> str:
        """Generate a summary of the theme cluster."""
        summary = [
            f"# Theme: {self.name}\n",
            f"{self.description}\n",
            "## Overview",
            f"- Notes: {len(self.notes)}",
            f"- Core Tags: {', '.join(f'#{tag}' for tag, _ in self.tags.most_common(5))}",
            "\n## Notes in this Theme"
        ]
        
        for note in sorted(self.notes, key=lambda x: x.title):
            relative_path = os.path.relpath(note.path, "..")
            summary.append(f"- [{note.title}]({relative_path})")
        
        if self.common_links:
            summary.extend([
                "\n## Common References",
                "These links appear in multiple notes:"
            ])
            for link in sorted(self.common_links):
                summary.append(f"- [[{link}]]")
        
        return '\n'.join(summary)

def collect_notes() -> List[Note]:
    """Collect all notes from the system."""
    notes = []
    
    for directory in [NOTES_DIR, PROJECTS_DIR]:
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                note = Note.from_file(file_path)
                if note:
                    notes.append(note)
    
    return notes

def build_similarity_matrix(notes: List[Note]) -> np.ndarray:
    """Build a similarity matrix between notes."""
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=1000,
        ngram_range=(1, 2)
    )
    
    # Prepare documents
    documents = [
        f"{note.title} {' '.join(note.tags)} {note.content}"
        for note in notes
    ]
    
    # Calculate TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity
    similarity = (tfidf_matrix * tfidf_matrix.T).toarray()
    
    return similarity

def find_clusters(notes: List[Note]) -> List[List[Note]]:
    """Find clusters of related notes."""
    # Build similarity matrix
    similarity_matrix = build_similarity_matrix(notes)
    
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    
    # Perform DBSCAN clustering
    clustering = DBSCAN(
        eps=1 - SIMILARITY_THRESHOLD,
        min_samples=MIN_THEME_SIZE,
        metric='precomputed'
    ).fit(distance_matrix)
    
    # Group notes by cluster
    clusters = defaultdict(list)
    for note, label in zip(notes, clustering.labels_):
        if label != -1:  # Ignore noise points
            clusters[label].append(note)
    
    return list(clusters.values())

def analyze_cluster(notes: List[Note]) -> ThemeCluster:
    """Analyze a cluster to determine its theme and characteristics."""
    # Count all tags in the cluster
    tag_counter = Counter()
    for note in notes:
        tag_counter.update(note.tags)
    
    # Use most common tags to name the theme
    top_tags = [tag for tag, _ in tag_counter.most_common(3)]
    theme_name = ' '.join(top_tags).title()
    
    # Create theme cluster
    cluster = ThemeCluster(
        name=theme_name,
        description=f"A collection of {len(notes)} notes related to {', '.join(top_tags)}."
    )
    
    # Add notes to cluster
    for note in notes:
        cluster.add_note(note)
    
    return cluster

def generate_theme_index(cluster: ThemeCluster) -> str:
    """Generate an index file for a theme."""
    return cluster.get_summary()

def main() -> None:
    """Main function to identify and analyze theme clusters."""
    print("Analyzing thematic clusters...")
    
    # Collect notes
    notes = collect_notes()
    print(f"Found {len(notes)} notes")
    
    # Find clusters
    print("Identifying clusters...")
    note_clusters = find_clusters(notes)
    print(f"Found {len(note_clusters)} thematic clusters")
    
    # Analyze each cluster
    themes = []
    for cluster_notes in note_clusters:
        theme = analyze_cluster(cluster_notes)
        themes.append(theme)
    
    # Generate theme indexes
    print("\nGenerating theme indexes...")
    for theme in themes:
        index_path = os.path.join(
            NOTES_DIR,
            "meta",
            f"theme-{theme.name.lower().replace(' ', '-')}.md"
        )
        
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, 'w') as f:
            f.write(generate_theme_index(theme))
        
        print(f"- Created index for theme: {theme.name}")
    
    # Generate master theme index
    master_index = [
        "# Thematic Clusters\n",
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Overview",
        f"Found {len(themes)} thematic clusters in your notes:\n"
    ]
    
    for theme in sorted(themes, key=lambda x: len(x.notes), reverse=True):
        master_index.extend([
            f"### {theme.name}",
            f"- Notes: {len(theme.notes)}",
            f"- Core Tags: {', '.join(f'#{tag}' for tag, _ in theme.tags.most_common(3))}",
            f"- [View Full Analysis](theme-{theme.name.lower().replace(' ', '-')}.md)\n"
        ])
    
    master_index_path = os.path.join(NOTES_DIR, "meta", "theme-clusters.md")
    with open(master_index_path, 'w') as f:
        f.write('\n'.join(master_index))
    
    print(f"\nMaster theme index created: {master_index_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error analyzing themes: {e}")
