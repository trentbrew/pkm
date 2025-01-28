#!/usr/bin/env python3
"""
daily_review.py: Facilitate daily and weekly review processes.

This script helps manage daily logs, summarizes recent activity,
and prompts for necessary review actions.
"""

import os
import yaml
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
DAILY_DIR = "../01-Daily"
NOTES_DIR = "../02-Notes"
PROJECTS_DIR = "../03-Projects"
REVIEW_TEMPLATE = os.path.join(DAILY_DIR, "review-template.md")

def get_recent_files(days: int = 7) -> List[Tuple[str, datetime.datetime]]:
    """Get files modified in the last N days."""
    recent_files = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    
    for directory in [DAILY_DIR, NOTES_DIR, PROJECTS_DIR]:
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

def get_unreviewed_logs() -> List[str]:
    """Find daily logs that haven't been reviewed."""
    unreviewed = []
    
    for file in os.listdir(DAILY_DIR):
        if not file.endswith('.md') or file in ['review-template.md', 'chaos-pit.md']:
            continue
        
        file_path = os.path.join(DAILY_DIR, file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file has been reviewed
            if '- [x] Daily review completed' not in content:
                unreviewed.append(file_path)
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
    
    return unreviewed

def create_daily_log() -> str:
    """Create today's daily log if it doesn't exist."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_path = os.path.join(DAILY_DIR, f"{today}.md")
    
    if not os.path.exists(log_path):
        # Get template content
        template_content = ""
        if os.path.exists(REVIEW_TEMPLATE):
            with open(REVIEW_TEMPLATE, 'r') as f:
                template_content = f.read()
        
        # Create daily log with YAML frontmatter
        content = [
            "---",
            "date: " + today,
            "type: daily-log",
            "tags: ['daily']",
            "---",
            "",
            f"# Daily Log: {datetime.datetime.now().strftime('%B %d, %Y')}",
            "",
            "## Morning",
            "- [ ] Review yesterday's unfinished items",
            "- [ ] Process inbox/chaos-pit",
            "- [ ] Set today's priorities",
            "",
            "## Tasks",
            "- [ ] ",
            "",
            "## Notes",
            "- ",
            "",
            "## Evening Review",
            "- [ ] Process today's notes",
            "- [ ] Move actionable items to appropriate locations",
            "- [ ] Update project statuses",
            "- [ ] Clear chaos-pit",
            "- [ ] Daily review completed"
        ]
        
        with open(log_path, 'w') as f:
            f.write('\n'.join(content))
    
    return log_path

def generate_review_summary() -> str:
    """Generate a summary of recent activity."""
    summary = ["# Review Summary\n"]
    
    # Get recent activity
    recent_files = get_recent_files(7)
    summary.extend([
        "## Recent Activity",
        f"Last 7 days ({len(recent_files)} files):\n"
    ])
    
    # Group by day
    by_day = {}
    for file_path, modified_time in recent_files:
        day = modified_time.strftime('%Y-%m-%d')
        if day not in by_day:
            by_day[day] = []
        by_day[day].append((file_path, modified_time))
    
    for day in sorted(by_day.keys(), reverse=True):
        summary.append(f"\n### {day}")
        for file_path, modified_time in by_day[day]:
            relative_path = os.path.relpath(file_path, "..")
            summary.append(f"- `{relative_path}`")
    
    # Check unreviewed logs
    unreviewed = get_unreviewed_logs()
    if unreviewed:
        summary.extend([
            "\n## Pending Reviews",
            "The following daily logs need review:\n"
        ])
        for log in unreviewed:
            relative_path = os.path.relpath(log, "..")
            summary.append(f"- `{relative_path}`")
    
    # Add weekly review section if it's Sunday
    if datetime.datetime.now().weekday() == 6:
        summary.extend([
            "\n## Weekly Review Tasks",
            "- [ ] Review all daily logs",
            "- [ ] Update index and tags",
            "- [ ] Archive completed items",
            "- [ ] Plan next week's priorities"
        ])
    
    return '\n'.join(summary)

def main() -> None:
    """Main function to run daily review process."""
    print("Running daily review process...")
    
    # Create today's log if needed
    daily_log = create_daily_log()
    print(f"\nToday's log: {os.path.relpath(daily_log, '..')}")
    
    # Generate review summary
    summary = generate_review_summary()
    summary_path = os.path.join(DAILY_DIR, "review-summary.md")
    
    with open(summary_path, 'w') as f:
        f.write(summary)
    
    print(f"Review summary generated: {os.path.relpath(summary_path, '..')}")
    
    # Check for unreviewed logs
    unreviewed = get_unreviewed_logs()
    if unreviewed:
        print(f"\nFound {len(unreviewed)} unreviewed daily logs")
        print("Run these commands to process them:")
        for log in unreviewed:
            print(f"- python chaos_extractor.py {log}")
    
    print("\nDaily review setup complete!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during daily review: {e}")
