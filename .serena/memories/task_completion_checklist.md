# Task Completion Checklist

## When a Development Task is Completed

### 1. Testing
```bash
# Run all tests to ensure nothing is broken
uv run pytest

# Run specific tests if working on particular functionality
uv run pytest tests/test_pa_api_client.py -v
```

### 2. Quality Assurance
- Validate configuration before running tools
- Check that required API credentials are properly set
- Follow the 5-phase workflow strictly for article creation
- Use quality checklists in `checklists/` directory
- Target minimum 80/100 quality score

### 3. Affiliate Compliance
- Ensure proper affiliate disclosures
- Maintain Amazon ToS compliance
- Validate affiliate links using tools

### 4. Content Validation (for Article Projects)
- Verify all information comes from research reports only
- Ensure all information has proper sources (ASIN codes, citations)
- Remove any uncertain or unverifiable information
- Check persona alignment

### 5. Security Check
- Never commit sensitive credentials to repository
- Use environment variables for API keys
- Validate that `config/settings.yaml` doesn't contain hardcoded credentials

### 6. Documentation
- Update relevant documentation if new features added
- Follow template-driven approach for consistency
- Maintain accuracy over completeness

## Article-Specific Completion Steps
1. Run through quality checklist
2. Validate affiliate links work correctly
3. Ensure SEO optimization
4. Verify Sakura Checker results for products
5. Confirm persona alignment