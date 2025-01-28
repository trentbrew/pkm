# Personal Knowledge Management (PKM)

A powerful, scalable system for managing your knowledge, projects, and ideas. This system helps you transform scattered thoughts into structured, actionable insights while maintaining flexibility and ease of use.

## Features
- **Atomic Note System**: Capture and interlink ideas with ease
- **Real-Time LLM Integration**: Use AI to retrieve, expand, and synthesize insights
- **Automation Toolbox**: Scripts that handle grunt work so you can focus on creativity
- **Chaos Buffer**: Dump raw ideas without judgment and process them later
- **Dynamic Organization**: A system that evolves with you and adapts to your needs

## Why Use This System?
Built around the principles of simplicity, scalability, and adaptability, this PKM system helps you:
- Turn random thoughts into actionable insights
- Surface connections between ideas you didn't know were there
- Maintain clarity even when life gets messy
- Work with AI to make your thinking sharper, faster, and smarter

## Directory Structure

Here's how the PKM system organizes your knowledge:

```plaintext
/pkm
├── /00-Index       # Mission control: centralizes navigation, tags, and priorities
├── /01-Daily       # Daily logs and chaos dumping ground
├── /02-Notes       # Atomic notes for ideas, concepts, and questions
├── /03-Projects    # Active workspaces for deliverables
├── /04-Resources   # Reference materials, datasets, and external links
├── /05-Archive     # Graveyard for dormant notes and projects
└── /Scripts        # Automation scripts to keep the system humming
```

### 1. `/00-Index`: Mission Control
- **Purpose**: Centralize navigation, priorities, and metadata
- **Key Files**:
  - `index.md`: High-level overview of the system, updated dynamically
  - `tags.md`: Master list of tags and their meanings
  - `related.md`: Summarized relationships between key topics
  - `stats.md`: Optional system usage stats

### 2. `/01-Daily`: Capturing the Chaos
- **Purpose**: A safe space to dump ideas, notes, and random thoughts
- **Key Files**:
  - `YYYY-MM-DD.md`: Daily logs for thoughts, notes, and tasks
  - `chaos-pit.md`: A catch-all for unstructured ideas
  - `review-template.md`: A guide for processing daily/weekly logs

### 3. `/02-Notes`: The Knowledge Engine
- **Purpose**: Your atomic knowledge base, built for interconnection
- **Structure**:
  - `/concepts`: Individual ideas and insights
  - `/questions`: Open-ended thoughts and philosophical musings
- **Features**:
  - All notes include YAML metadata:
    ```yaml
    title: "Example Note"
    tags: ["#topic", "#category"]
    created: "2025-01-27"
    updated: "2025-01-28"
    related: ["[[related-note.md]]"]
    ```

### 4. `/03-Projects`: Work in Progress
- **Purpose**: Actionable workspaces for projects and deliverables
- **Structure**:
  - One folder per project
  - Logs, drafts, and final deliverables
- **Workflow**:
  - Link project-related notes from `/02-Notes`
  - Archive dormant projects in `/05-Archive/projects`

### 5. `/04-Resources`: Your External Brain
- **Purpose**: Store reference materials, datasets, and external files
- **Structure**:
  - `/papers`: PDFs or research papers
  - `/diagrams`: Visual assets
  - `/data`: CSVs, spreadsheets, or other datasets

### 6. `/05-Archive`: The Knowledge Graveyard
- **Purpose**: Preserve inactive projects and notes without cluttering your workspace
- **Structure**:
  - `/projects`: Archived project folders
  - `/notes`: Archived atomic notes

### 7. `/Scripts`: Automation Toolbox
- **Purpose**: Keep the system running smoothly with automation
- **Core Scripts**:
  - `archive_stale_notes.py`: Archive unused content
  - `generate_index.py`: Update system indexes
  - `tag_audit.py`: Maintain tag consistency
  - `chaos_extractor.py`: Process unstructured thoughts
  - `daily_review.py`: Facilitate reviews
  - `orphan_notes.py`: Find disconnected notes
  - `link_audit.py`: Verify note connections
  - `project_cleaner.py`: Archive inactive projects
  - `project_template_generator.py`: Create new projects
  - `generate_stats.py`: System analytics
  - `theme_clustering.py`: Find note clusters

## Daily Workflow

1. **Morning**:
   - Open today's daily log in `/01-Daily/YYYY-MM-DD.md`
   - Review yesterday's unfinished items
   - Process any items in `chaos-pit.md`

2. **Throughout the Day**:
   - Capture thoughts and ideas in `chaos-pit.md`
   - Create atomic notes in `/02-Notes` for important concepts
   - Link related notes using wiki-style links `[[note-name]]`

3. **Evening Review**:
   - Process remaining items in `chaos-pit.md`
   - Update project statuses
   - Run maintenance scripts as needed

4. **Weekly Review**:
   - Archive completed projects
   - Audit and clean tags
   - Generate fresh indexes
   - Review and cluster related notes

## Tips for Success
1. **Start Simple**: Build as you go. Don't over-engineer before you start
2. **Embrace Chaos**: Use `chaos-pit.md` freely. Process it during reviews
3. **Link Generously**: Create connections between notes to build a knowledge graph
4. **Prune Regularly**: Archive or delete outdated content to maintain clarity

## Setup
1. Install Python dependencies:
   ```bash
   cd Scripts
   pip install -r requirements.txt
   ```

2. Run the initial setup:
   ```bash
   python generate_index.py
   ```

## Future Plans
- Enhanced LLM integration for smarter note processing
- Advanced visualization tools for note relationships
- Improved multimedia content handling
- Real-time collaboration features

## License
This system is open source and free to adapt to your needs. Attribution is appreciated but not required.
