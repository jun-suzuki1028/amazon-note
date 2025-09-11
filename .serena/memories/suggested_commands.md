# Suggested Commands for Amazon Note Rank

## Package Management (UV-based)
```bash
# Install dependencies
uv sync

# Add new packages
uv add package_name

# Run Python scripts
uv run python main.py
uv run python tools/affiliate_link_generator_integrated.py --project-id "project-name"
```

## Testing Commands
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_pa_api_client.py -v

# Run with verbose output
python -m pytest tests/test_pa_api_client.py -v
```

## Core Tool Commands
```bash
# Generate affiliate links for a project
python3 tools/affiliate_link_generator_integrated.py --project-id "gaming-monitor-fighter-2025-01-07"

# Generate affiliate links for specific article
python3 tools/affiliate_link_generator_integrated.py --article-path "path/to/article.md"
```

## Development Workflow
1. Create new project under `projects/{project-id}/`
2. Follow 5-phase workflow:
   - Persona Creation (30-45min)
   - Prompt Generation (20-30min) 
   - DeepResearch Execution (60-90min)
   - Article Generation (45-60min)
   - Quality Check & Finalization (30-45min)

## Quality Assurance
- Always run quality checks using checklists in `checklists/`
- Target minimum 80/100 quality score
- Validate affiliate compliance
- Use Sakura Checker for product credibility