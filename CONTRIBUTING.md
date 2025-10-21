# Contributing to RAG Chatbot

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- **Bug Reports**: Found a bug? Open an issue with details
- **Feature Requests**: Have an idea? Share it in the issues
- **Documentation**: Improve README, add examples, fix typos
- **Code**: Submit pull requests with bug fixes or new features
- **Testing**: Help test on different platforms and configurations

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/rag-chatbot.git
cd rag-chatbot
```

### 2. Set Up Development Environment

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Start services
docker-compose up -d

# Pull the model
docker exec openwebui-ollama-1 ollama pull llama3
```

### 3. Make Your Changes

Create a new branch for your feature or fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 4. Test Your Changes

```bash
# Test the document loader
docker exec openwebui-backend-1 python loader.py

# Test the API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "test question"}'

# Check logs
docker-compose logs -f backend
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: description of what you added"
# or
git commit -m "Fix: description of what you fixed"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a pull request on GitHub.

## 📋 Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Include type hints where appropriate
- Keep functions focused and under 50 lines when possible

Example:
```python
def process_document(file_path: str, chunk_size: int = 512) -> List[Document]:
    """
    Process a document and split it into chunks.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of each chunk in tokens
        
    Returns:
        List of Document objects
    """
    # Implementation
    pass
```

### Comments

- Write self-documenting code when possible
- Add comments for complex logic
- Keep comments up to date with code changes

### Error Handling

Always include proper error handling:

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

## 🧪 Testing

### Manual Testing Checklist

Before submitting a PR, ensure:

- [ ] All services start successfully with `docker-compose up -d`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Document loader works with test documents
- [ ] `/ask` endpoint returns valid responses
- [ ] No errors in container logs
- [ ] Documentation is updated if needed

### Adding Test Documents

Place test files in `data/docs/test/` (not tracked by git):

```bash
mkdir -p data/docs/test
cp sample-test.pdf data/docs/test/
docker exec openwebui-backend-1 python loader.py
```

## 📝 Pull Request Guidelines

### PR Title Format

- `Feature: Add support for X`
- `Fix: Resolve issue with Y`
- `Docs: Update README for Z`
- `Refactor: Improve performance of W`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
Describe how you tested this

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tested locally
- [ ] No new warnings/errors
```

## 🐛 Bug Reports

When reporting bugs, include:

1. **Environment**: OS, Docker version, available RAM
2. **Steps to Reproduce**: Exact steps to trigger the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Logs**: Relevant error messages or logs
6. **Screenshots**: If applicable

Example:
```markdown
**Environment**: Ubuntu 22.04, Docker 24.0.2, 16GB RAM

**Steps to Reproduce**:
1. Start services with `docker-compose up -d`
2. Run `docker exec openwebui-backend-1 python loader.py`
3. Upload a 50MB PDF

**Expected**: Document should be indexed successfully

**Actual**: Process hangs after "Loading documents..."

**Logs**:
```
ERROR - Out of memory
```
```

## 💡 Feature Requests

For feature requests, describe:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other ways to achieve this?
4. **Impact**: Who benefits from this feature?

## 🏗️ Architecture Changes

For significant architectural changes:

1. Open an issue first to discuss the approach
2. Update `ARCHITECTURE.md` if needed
3. Consider backward compatibility
4. Update documentation

## 📚 Documentation

Good documentation includes:

- **README.md**: User-facing setup and usage
- **ARCHITECTURE.md**: Technical details
- **Code comments**: In-line explanations
- **Docstrings**: Function and class documentation

## 🎨 UI/UX Contributions

For Open WebUI customizations:

1. Test on multiple screen sizes
2. Ensure accessibility (keyboard navigation, screen readers)
3. Maintain consistent styling
4. Add screenshots to PR

## 🔒 Security

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainers directly
3. Include details and steps to reproduce
4. Wait for confirmation before disclosing

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

All contributors will be recognized in the project README. Thank you for making this project better!

## 💬 Questions?

- Open a discussion on GitHub
- Check existing issues and PRs
- Review documentation

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Other unprofessional conduct

---

**Happy Contributing! 🚀**
