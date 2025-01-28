#!/usr/bin/env python3
"""
generate_stats.py: Generate system-wide statistics and analytics.

This script analyzes the entire Cognet system to provide insights about
usage patterns, note relationships, and system health.
"""

import os
import re
import yaml
import datetime
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configuration
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
DAILY_DIR = "../01-Daily"
ARCHIVE_DIR = "../05-Archive"

class SystemStats:
    """Collect and analyze system statistics."""
    def __init__(self):
        self.total_notes = 0
        self.total_projects = 0
        self.total_daily_logs = 0
        self.archived_items = 0
        self.tags = Counter()
        self.links = defaultdict(set)
        self.modification_dates = []
        self.file_sizes = []
        self.activity_by_day = Counter()
    
    def analyze_file(self, file_path: str) -> None:
        """Analyze a single file for statistics."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count tags
            if content.startswith('---'):
                try:
                    _, fm, content = content.split('---', 2)
                    metadata = yaml.safe_load(fm)
                    if metadata and 'tags' in metadata:
                        for tag in metadata['tags']:
                            self.tags[tag] += 1
                except Exception:
                    pass
            
            # Count inline tags
            inline_tags = re.findall(r'#(\w+)', content)
            for tag in inline_tags:
                self.tags[tag] += 1
            
            # Count wiki-style links
            links = re.findall(r'\[\[(.*?)\]\]', content)
            for link in links:
                self.links[file_path].add(link)
            
            # Get file stats
            stat = os.stat(file_path)
            self.file_sizes.append(stat.st_size)
            mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            self.modification_dates.append(mod_time)
            self.activity_by_day[mod_time.date()] += 1
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

def collect_stats() -> SystemStats:
    """Collect statistics from all system components."""
    stats = SystemStats()
    
    # Analyze notes
    for root, _, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                stats.total_notes += 1
                stats.analyze_file(os.path.join(root, file))
    
    # Analyze projects
    for root, dirs, files in os.walk(PROJECTS_DIR):
        if root == PROJECTS_DIR:
            stats.total_projects = len(dirs)
        for file in files:
            if file.endswith('.md'):
                stats.analyze_file(os.path.join(root, file))
    
    # Count daily logs
    if os.path.exists(DAILY_DIR):
        stats.total_daily_logs = len([
            f for f in os.listdir(DAILY_DIR)
            if f.endswith('.md') and f not in ['review-template.md', 'chaos-pit.md']
        ])
    
    # Count archived items
    if os.path.exists(ARCHIVE_DIR):
        for root, _, files in os.walk(ARCHIVE_DIR):
            stats.archived_items += len([f for f in files if f.endswith('.md')])
    
    return stats

def calculate_activity_metrics(stats: SystemStats) -> Dict:
    """Calculate activity-based metrics."""
    metrics = {}
    
    # Calculate active days
    if stats.activity_by_day:
        active_days = len(stats.activity_by_day)
        total_days = (max(stats.activity_by_day) - min(stats.activity_by_day)).days + 1
        metrics['activity_ratio'] = active_days / total_days if total_days > 0 else 0
        
        # Calculate activity streak
        current_date = datetime.date.today()
        streak = 0
        while current_date in stats.activity_by_day:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        metrics['current_streak'] = streak
    
    # Calculate connection density
    if stats.total_notes > 0:
        total_links = sum(len(links) for links in stats.links.values())
        metrics['connection_density'] = total_links / stats.total_notes
    
    return metrics

def generate_report(stats: SystemStats) -> str:
    """Generate a detailed statistical report."""
    metrics = calculate_activity_metrics(stats)
    
    report = [
        "# Cognet System Statistics\n",
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## System Overview",
        f"- Total Notes: {stats.total_notes}",
        f"- Active Projects: {stats.total_projects}",
        f"- Daily Logs: {stats.total_daily_logs}",
        f"- Archived Items: {stats.archived_items}\n",
        "## Activity Metrics",
        f"- Current Streak: {metrics.get('current_streak', 0)} days",
        f"- Activity Ratio: {metrics.get('activity_ratio', 0):.2%}",
        f"- Connection Density: {metrics.get('connection_density', 0):.2f} links per note\n",
        "## Popular Tags"
    ]
    
    # Add top tags
    for tag, count in stats.tags.most_common(10):
        report.append(f"- #{tag} ({count} uses)")
    
    # Add file statistics
    if stats.file_sizes:
        avg_size = sum(stats.file_sizes) / len(stats.file_sizes)
        report.extend([
            "\n## File Statistics",
            f"- Average File Size: {avg_size/1024:.1f} KB",
            f"- Total Files: {len(stats.file_sizes)}"
        ])
    
    # Add recent activity
    if stats.modification_dates:
        report.extend([
            "\n## Recent Activity",
            "Last 7 days of activity:"
        ])
        
        today = datetime.date.today()
        for i in range(7):
            date = today - datetime.timedelta(days=i)
            count = stats.activity_by_day[date]
            report.append(
                f"- {date.strftime('%Y-%m-%d')}: "
                f"{count} {'files' if count != 1 else 'file'} modified"
            )
    
    # Add recommendations
    report.extend([
        "\n## System Health Recommendations",
        "1. " + get_health_recommendation(stats),
        "2. " + get_activity_recommendation(metrics),
        "3. " + get_organization_recommendation(stats)
    ])
    
    return '\n'.join(report)

def get_health_recommendation(stats: SystemStats) -> str:
    """Generate a system health recommendation."""
    if stats.archived_items > stats.total_notes * 0.5:
        return "Consider reviewing archived items for potential restoration or deletion"
    elif stats.total_notes > 100 and len(stats.tags) < stats.total_notes * 0.3:
        return "Add more tags to improve note discoverability"
    else:
        return "System appears healthy, maintain current practices"

def get_activity_recommendation(metrics: Dict) -> str:
    """Generate an activity-based recommendation."""
    if metrics.get('activity_ratio', 0) < 0.3:
        return "Increase system usage frequency to maintain knowledge base"
    elif metrics.get('current_streak', 0) < 3:
        return "Build a daily note-taking habit to improve system value"
    else:
        return "Good activity level, focus on deepening note connections"

def get_organization_recommendation(stats: SystemStats) -> str:
    """Generate an organization-based recommendation."""
    if stats.total_projects > 10 and stats.archived_items < stats.total_projects * 0.2:
        return "Review and archive completed or inactive projects"
    elif len(stats.links) < stats.total_notes * 0.5:
        return "Create more connections between related notes"
    else:
        return "Organization is good, focus on content quality"

def main() -> None:
    """Main function to generate system statistics."""
    print("Analyzing system statistics...")
    
    # Collect and analyze stats
    stats = collect_stats()
    
    # Generate report
    report = generate_report(stats)
    report_path = os.path.join(NOTES_DIR, "meta", "system-stats.md")
    
    # Save report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nStatistics generated and saved to: {report_path}")
    print(f"Total notes: {stats.total_notes}")
    print(f"Active projects: {stats.total_projects}")
    print(f"Most used tag: #{stats.tags.most_common(1)[0][0]}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error generating statistics: {e}")
