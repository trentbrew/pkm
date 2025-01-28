#!/usr/bin/env python3
"""
project_template_generator.py: Create new project directories with consistent structure.

This script generates project folders with standardized templates and structure,
ensuring consistency across projects.
"""

import os
import yaml
import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
PROJECTS_DIR = "../03-Projects"
PROJECT_TYPES = {
    'personal': 'Personal project',
    'client': 'Client work',
    'research': 'Research project',
    'experiment': 'Experimental project'
}

class ProjectTemplate:
    """Base class for project templates."""
    def __init__(
        self,
        name: str,
        description: str,
        project_type: str,
        tags: List[str]
    ):
        self.name = name
        self.description = description
        self.project_type = project_type
        self.tags = tags
        self.created_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    def get_readme_content(self) -> str:
        """Generate README.md content."""
        return '\n'.join([
            "---",
            f"title: {self.name}",
            f"type: {self.project_type}",
            f"created: {self.created_date}",
            f"status: active",
            f"tags: {self.tags}",
            "---",
            "",
            f"# {self.name}",
            "",
            f"{self.description}",
            "",
            "## Overview",
            "- **Status**: Active",
            f"- **Type**: {self.project_type}",
            f"- **Created**: {self.created_date}",
            "",
            "## Project Structure",
            "- `/docs` - Documentation and notes",
            "- `/assets` - Project assets and resources",
            "- `/archive` - Archived or deprecated items",
            "",
            "## Goals",
            "1. ",
            "",
            "## Timeline",
            "- [ ] Phase 1:",
            "- [ ] Phase 2:",
            "- [ ] Phase 3:",
            "",
            "## Notes",
            "- "
        ])
    
    def get_tasks_content(self) -> str:
        """Generate tasks.md content."""
        return '\n'.join([
            "---",
            f"project: {self.name}",
            f"created: {self.created_date}",
            "type: task-list",
            "---",
            "",
            "# Project Tasks",
            "",
            "## Active Tasks",
            "- [ ] Set up project structure",
            "- [ ] Define initial goals and timeline",
            "- [ ] Create project documentation",
            "",
            "## Backlog",
            "- ",
            "",
            "## Completed Tasks",
            "- [x] Initialize project"
        ])
    
    def get_notes_content(self) -> str:
        """Generate notes.md content."""
        return '\n'.join([
            "---",
            f"project: {self.name}",
            f"created: {self.created_date}",
            "type: project-notes",
            "---",
            "",
            "# Project Notes",
            "",
            "## Important Links",
            "- ",
            "",
            "## Meeting Notes",
            "### Initial Planning",
            "- Date: ",
            "- Attendees: ",
            "- Key Points:",
            "  - ",
            "",
            "## Ideas and Thoughts",
            "- "
        ])

class PersonalProjectTemplate(ProjectTemplate):
    """Template for personal projects."""
    def __init__(self, name: str, description: str):
        super().__init__(
            name,
            description,
            'personal',
            ['project-personal']
        )
    
    def get_readme_content(self) -> str:
        base_content = super().get_readme_content()
        return base_content + "\n\n## Personal Goals\n- "

class ClientProjectTemplate(ProjectTemplate):
    """Template for client projects."""
    def __init__(
        self,
        name: str,
        description: str,
        client_name: str,
        deadline: str
    ):
        super().__init__(
            name,
            description,
            'client',
            ['project-client']
        )
        self.client_name = client_name
        self.deadline = deadline
    
    def get_readme_content(self) -> str:
        base_content = super().get_readme_content()
        return base_content + '\n'.join([
            "",
            "## Client Information",
            f"- **Client**: {self.client_name}",
            f"- **Deadline**: {self.deadline}",
            "",
            "## Requirements",
            "- ",
            "",
            "## Deliverables",
            "- "
        ])

def create_project_structure(template: ProjectTemplate, base_path: str) -> None:
    """Create project directory structure with template files."""
    # Create main project directory
    project_dir = os.path.join(base_path, template.name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = ['docs', 'assets', 'archive']
    for subdir in subdirs:
        os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)
    
    # Create README.md
    with open(os.path.join(project_dir, 'README.md'), 'w') as f:
        f.write(template.get_readme_content())
    
    # Create tasks.md
    with open(os.path.join(project_dir, 'tasks.md'), 'w') as f:
        f.write(template.get_tasks_content())
    
    # Create notes.md
    with open(os.path.join(project_dir, 'notes.md'), 'w') as f:
        f.write(template.get_notes_content())

def get_user_input() -> Dict:
    """Get project information from user."""
    print("\nProject Template Generator\n")
    
    # Get basic project info
    project_name = input("Project name: ").strip()
    description = input("Project description: ").strip()
    
    # Select project type
    print("\nProject types:")
    for key, value in PROJECT_TYPES.items():
        print(f"- {key}: {value}")
    
    project_type = input("\nSelect project type: ").strip().lower()
    
    # Get additional info for client projects
    if project_type == 'client':
        client_name = input("Client name: ").strip()
        deadline = input("Project deadline (YYYY-MM-DD): ").strip()
        return {
            'name': project_name,
            'description': description,
            'type': project_type,
            'client_name': client_name,
            'deadline': deadline
        }
    
    return {
        'name': project_name,
        'description': description,
        'type': project_type
    }

def main() -> None:
    """Main function to generate project structure."""
    try:
        # Get project information
        info = get_user_input()
        
        # Create appropriate template
        if info['type'] == 'client':
            template = ClientProjectTemplate(
                info['name'],
                info['description'],
                info['client_name'],
                info['deadline']
            )
        else:
            template = PersonalProjectTemplate(
                info['name'],
                info['description']
            )
        
        # Create project structure
        create_project_structure(template, PROJECTS_DIR)
        
        print(f"\nProject created successfully: {info['name']}")
        print(f"Location: {os.path.join(PROJECTS_DIR, info['name'])}")
    
    except KeyboardInterrupt:
        print("\nProject creation cancelled.")
    except Exception as e:
        print(f"Error creating project: {e}")

if __name__ == "__main__":
    main()
