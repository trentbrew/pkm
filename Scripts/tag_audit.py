#!/usr/bin/env python3
"""
tag_audit.py: Analyze and optimize tag usage across the Cognet system.

This script identifies redundant, unused, or overused tags and suggests
improvements to maintain a clean and efficient tagging system.
"""

import os
import yaml
import difflib
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Configuration
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
MIN_TAG_USAGE = 2  # Minimum number of files per tag
MAX_TAG_SIMILARITY = 0.85  # Threshold for suggesting tag merges

def collect_tag_usage() -> Dict[str, List[str]]:
    """Collect all tags and their associated files."""
    tags = defaultdict(list)
    
    for directory in [NOTES_DIR, PROJECTS_DIR]:
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith('.md'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    if content.startswith('---'):
                        _, fm, _ = content.split('---', 2)
                        metadata = yaml.safe_load(fm)
                        
                        if metadata and 'tags' in metadata:
                            for tag in metadata['tags']:
                                tags[tag].append(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return tags

def find_unused_tags(tags: Dict[str, List[str]]) -> List[str]:
    """Find tags that are used less than MIN_TAG_USAGE times."""
    return [
        tag for tag, files in tags.items()
        if len(files) < MIN_TAG_USAGE
    ]

def find_similar_tags(tags: Dict[str, List[str]]) -> List[Tuple[str, str, float]]:
    """Find pairs of tags that are similar and might be candidates for merging."""
    similar_pairs = []
    tag_list = list(tags.keys())
    
    for i, tag1 in enumerate(tag_list):
        for tag2 in tag_list[i+1:]:
            similarity = difflib.SequenceMatcher(None, tag1, tag2).ratio()
            if similarity > MAX_TAG_SIMILARITY:
                similar_pairs.append((tag1, tag2, similarity))
    
    return sorted(similar_pairs, key=lambda x: x[2], reverse=True)

def analyze_tag_patterns(tags: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Analyze tag patterns and suggest improvements."""
    suggestions = defaultdict(list)
    
    # Check for inconsistent capitalization
    lowercase_map = defaultdict(list)
    for tag in tags:
        lowercase_map[tag.lower()].append(tag)
    
    for variants in lowercase_map.values():
        if len(variants) > 1:
            suggestions['capitalization'].extend(variants)
    
    # Check for singular/plural inconsistencies
    for tag in tags:
        if tag.endswith('s'):
            singular = tag[:-1]
            if singular in tags:
                suggestions['singular_plural'].append((singular, tag))
    
    # Check for prefix/suffix patterns
    prefixes = defaultdict(list)
    for tag in tags:
        parts = tag.split('-')
        if len(parts) > 1:
            prefixes[parts[0]].append(tag)
    
    for prefix, prefix_tags in prefixes.items():
        if len(prefix_tags) >= 3:  # If prefix is used in 3+ tags
            suggestions['prefix_patterns'].extend(prefix_tags)
    
    return suggestions

def generate_report(
    tags: Dict[str, List[str]],
    unused_tags: List[str],
    similar_tags: List[Tuple[str, str, float]],
    pattern_suggestions: Dict[str, List[str]]
) -> str:
    """Generate a detailed audit report."""
    report = ["# Tag Audit Report\n"]
    
    # Unused tags
    report.extend([
        "## Unused or Rare Tags\n",
        "Tags used in fewer than {} files:\n".format(MIN_TAG_USAGE)
    ])
    for tag in unused_tags:
        files = tags[tag]
        report.append(f"- #{tag} ({len(files)} files)")
        for file in files:
            relative_path = os.path.relpath(file, "..")
            report.append(f"  - `{relative_path}`")
    
    # Similar tags
    report.extend([
        "\n## Potentially Redundant Tags\n",
        "Tags that might be consolidated:\n"
    ])
    for tag1, tag2, similarity in similar_tags:
        report.append(
            f"- #{tag1} ↔ #{tag2} "
            f"(similarity: {similarity:.2%}, "
            f"files: {len(tags[tag1])} ↔ {len(tags[tag2])})"
        )
    
    # Pattern suggestions
    report.append("\n## Tag Pattern Analysis\n")
    
    if pattern_suggestions['capitalization']:
        report.extend([
            "### Inconsistent Capitalization\n",
            "Standardize capitalization for these tag groups:\n"
        ])
        for variants in pattern_suggestions['capitalization']:
            report.append(f"- {', '.join(f'#{v}' for v in variants)}")
    
    if pattern_suggestions['singular_plural']:
        report.extend([
            "\n### Singular/Plural Inconsistencies\n",
            "Choose one form for these tags:\n"
        ])
        for singular, plural in pattern_suggestions['singular_plural']:
            report.append(f"- #{singular} ↔ #{plural}")
    
    if pattern_suggestions['prefix_patterns']:
        report.extend([
            "\n### Common Prefixes\n",
            "Consider standardizing these tag groups:\n"
        ])
        for tag in pattern_suggestions['prefix_patterns']:
            report.append(f"- #{tag}")
    
    # Add recommendations
    report.extend([
        "\n## Recommendations\n",
        "1. Remove or consolidate unused tags",
        "2. Merge similar tags to reduce redundancy",
        "3. Standardize capitalization and singular/plural forms",
        "4. Use consistent prefixes for related tags"
    ])
    
    return '\n'.join(report)

def main() -> None:
    """Main function to run the tag audit."""
    print("Running tag audit...")
    
    # Collect and analyze tags
    tags = collect_tag_usage()
    unused_tags = find_unused_tags(tags)
    similar_tags = find_similar_tags(tags)
    pattern_suggestions = analyze_tag_patterns(tags)
    
    # Generate and save report
    report = generate_report(tags, unused_tags, similar_tags, pattern_suggestions)
    report_path = os.path.join(NOTES_DIR, "meta", "tag-audit-report.md")
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Print summary
    print(f"\nFound {len(unused_tags)} unused tags")
    print(f"Found {len(similar_tags)} similar tag pairs")
    print(f"\nFull report saved to: {report_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during tag audit: {e}")
