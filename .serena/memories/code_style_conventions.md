# Code Style and Conventions

## General Principles
- **Accuracy is paramount**: Never sacrifice accuracy for completeness
- **Template-driven development**: Use standardized templates for consistency
- **Evidence-based**: All information must have verifiable sources

## Python Code Style
- **Python Version**: 3.12+
- **Testing Framework**: pytest with TDD principles
- **Class Naming**: `Test{ClassName}` for test classes
- **Method Naming**: `test_{functionality}` for test methods
- **Error Handling**: Comprehensive error handling with custom exceptions:
  - `PAAPIAuthenticationError`
  - `PAAPIRateLimitError` 
  - `PAAPIConfigError`
  - `PAAPINetworkError`

## Project Structure Conventions
- Each article project under `projects/{project-id}/`
- Standard folder structure:
  - `persona/` - Target reader personas
  - `prompts/` - Generated DeepResearch prompts
  - `research/` - Research data and results
  - `articles/` - Draft and final articles
  - `meta/` - Project metadata and status

## Configuration Management
- Central configuration in `config/settings.yaml`
- Environment variables for sensitive data (AWS credentials)
- Use `.env` files for local overrides

## Content Creation Rules (Japanese)
### 記事作成時の厳格なルール
1. **調査レポートに記載された情報のみを使用する**
2. **すべての情報に根拠が必要**
3. **不確実な情報の扱い**: 確認できない情報は含めない