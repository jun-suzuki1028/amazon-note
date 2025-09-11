# Amazon Note Rank - Project Overview

## Purpose
AI Amazon Article Generator - An automated system for creating high-quality Amazon affiliate ranking articles using Claude Code as the primary orchestration tool. The system generates 5 articles per week targeting ¥50,000 monthly affiliate revenue through a structured 5-phase workflow.

## Tech Stack
- **Language**: Python 3.12+
- **Package Manager**: UV (modern pip/poetry replacement)
- **Key Dependencies**:
  - boto3: Amazon PA-API 5.0 integration
  - pandas/numpy: Data processing and analysis
  - playwright: Browser automation for additional research
  - pyyaml: Configuration management
  - python-amazon-paapi: Amazon Product Advertising API integration
- **Testing**: pytest

## Architecture Overview
Template-driven, project-based architecture with standardized workflows:

### Main Components
- **Project Management**: Each article is a project under `projects/{project-id}/` with personas, prompts, research, articles, and metadata
- **Template System**: Standardized templates in `templates/` for personas, prompts, research, articles, and analytics  
- **Tool Suite**: Python utilities in `tools/` for Amazon PA-API integration, affiliate link generation, and content processing
- **Configuration**: Centralized YAML configuration in `config/settings.yaml` with affiliate settings, API credentials, and operational parameters

### Data Flow
Persona Creation → Prompt Generation → DeepResearch → Article Generation → Quality Check

## Key Features
- 5-phase article creation workflow
- Amazon PA-API integration for product data
- Quality assurance framework with scoring
- Gemini MCP integration for research automation
- Affiliate link generation tools
- Template-driven content generation