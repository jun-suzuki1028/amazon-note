# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Amazon Article Generator - An automated system for creating high-quality Amazon affiliate ranking articles using Claude Code as the primary orchestration tool. The system generates 5 articles per week targeting ¥50,000 monthly affiliate revenue through a structured 5-phase workflow.

## Core Architecture

The system follows a **template-driven, project-based architecture** with standardized workflows:

### Main Components
- **Project Management**: Each article is a project under `projects/{project-id}/` with personas, prompts, research, articles, and metadata
- **Template System**: Standardized templates in `templates/` for personas, prompts, research, articles, and analytics  
- **Tool Suite**: Python utilities in `tools/` for Amazon PA-API integration, affiliate link generation, and content processing
- **Configuration**: Centralized YAML configuration in `config/settings.yaml` with affiliate settings, API credentials, and operational parameters

### Data Flow Architecture
```
Persona Creation → Prompt Generation → DeepResearch → Article Generation → Quality Check
     ↓                ↓                  ↓              ↓                 ↓
templates/persona → templates/prompts → Gemini MCP → templates/article → checklists/
```

## Development Commands

### Package Management (UV-based)
```bash
# Install dependencies
uv sync

# Add new packages
uv add package_name

# Run Python scripts
uv run python main.py
uv run python tools/affiliate_link_generator_integrated.py --project-id "project-name"
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_pa_api_client.py -v

# Run with verbose output
python -m pytest tests/test_pa_api_client.py -v
```

### Core Tools Usage
```bash
# Generate affiliate links for a project
python3 tools/affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"

# Generate affiliate links for specific article
python3 tools/affiliate_link_generator_integrated.py --article-path "path/to/article.md"
```

## Project Structure Deep Dive

### Project Organization
Each article project follows this structure:
```
projects/{project-id}/
├── persona/           # Target reader personas
├── prompts/          # Generated DeepResearch prompts  
├── research/         # Research data and results
├── articles/         # Draft and final articles
└── meta/            # Project metadata and status
```

### Configuration Architecture
- **config/settings.yaml**: Master configuration with affiliate IDs, PA-API credentials, product criteria, and workflow settings
- **Environment Variables**: PA-API credentials via `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (preferred over hardcoded values)

### Critical Dependencies
- **boto3**: Amazon PA-API 5.0 integration
- **pandas/numpy**: Data processing and analysis
- **playwright**: Browser automation for additional research
- **pyyaml**: Configuration management

## Key Implementation Patterns

### Template-Driven Development
All content generation uses structured templates that ensure consistency and quality. Templates are located in `templates/` and include:
- Persona templates with detailed reader profiles
- Research prompt templates optimized for Gemini MCP
- Article templates with SEO optimization
- Analytics templates for performance tracking

### Error Handling Strategy
The system implements comprehensive error handling for:
- PA-API authentication and rate limiting (`PAAPIAuthenticationError`, `PAAPIRateLimitError`)
- Configuration validation (`PAAPIConfigError`)
- Network issues (`PAAPINetworkError`)

### TDD Implementation
Tests are structured following TDD principles with Red-Green-Refactor cycles. Test files use descriptive class and method names following the pattern `Test{ClassName}` and `test_{functionality}`.

## Workflow Integration

### 5-Phase Article Creation Process
1. **Persona Creation** (30-45min): Generate detailed reader profiles using `templates/persona/default_persona.md`
2. **Prompt Generation** (20-30min): Create DeepResearch prompts using `templates/prompts/research_prompts.md`
3. **DeepResearch Execution** (60-90min): Execute research via Gemini MCP or manual process
4. **Article Generation** (45-60min): Generate articles using `templates/article/ranking_article.md`
5. **Quality Check & Finalization** (30-45min): Quality assurance using checklists in `checklists/`

### Gemini MCP Integration
The system is designed to work with Gemini MCP for research automation but includes manual fallbacks. Research prompts are specifically optimized for Gemini MCP execution.

### Quality Assurance Framework
- Automated quality scoring (target: 80+ points)
- SEO optimization validation
- Sakura Checker integration for product credibility
- Persona alignment verification

## Security Considerations

**CRITICAL**: The current `config/settings.yaml` contains hardcoded API credentials which should be moved to environment variables immediately:
- Move AWS PA-API credentials to `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Use `.env` file or environment variables for sensitive configuration
- Add `config/settings.local.yaml` to `.gitignore` for local overrides

## Performance Targets

- **Weekly Output**: 5 high-quality ranking articles
- **Quality Threshold**: Minimum 80/100 quality score
- **Revenue Target**: ¥50,000 monthly affiliate revenue
- **Processing Time**: Complete article creation in 3-4 hours per article

## Important Notes for Claude Code

1. **Always validate configuration** before running tools - check that required API credentials are properly set
2. **Follow the 5-phase workflow** strictly - each phase builds on the previous one
3. **Use project-based organization** - create new projects under `projects/` with standardized folder structure
4. **Leverage templates consistently** - all content generation should use the provided templates
5. **Integration with Gemini MCP** - When available, use MCP for research automation; otherwise provide manual execution guidance
6. **Quality gates are mandatory** - never skip the quality check phase
7. **Maintain affiliate compliance** - ensure proper affiliate disclosures and Amazon ToS compliance