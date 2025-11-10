# GitHub Actions Workflow Troubleshooting Guide

## Overview
This guide documents common YAML syntax errors encountered in GitHub Actions workflows for the 3dPot project and their solutions.

## Common YAML Issues and Solutions

### 1. Heredoc Conflict in Multiline Strings

**Problem:** Using `cat > file << 'EOF'` (heredoc syntax) inside YAML multiline `run: |` blocks causes parsing conflicts.

**Error Message:**
```
Invalid workflow file: .github/workflows/python-tests.yml#L67
You have an error in your yaml syntax on line 67
```

**Root Cause:** 
YAML parser treats heredoc content as part of YAML structure, causing syntax errors.

**Solution:**
Replace heredoc with sequential `echo` commands:

```yaml
# ❌ Problematic (Heredoc)
cat > tests/test_basic.py << 'EOF'
import os

def test_project_structure():
    assert os.path.exists('README.md'), "README.md should exist"
EOF

# ✅ Solution (Echo commands)
echo 'import os' > tests/test_basic.py
echo '' >> tests/test_basic.py
echo 'def test_project_structure():' >> tests/test_basic.py
echo '    assert os.path.exists("README.md"), "README.md should exist"' >> tests/test_basic.py
```

### 2. Quote Escaping in YAML

**Problem:** Nested quotes in multiline strings can cause YAML parsing errors.

**Error Message:**
```yaml
def test_project_structure():
    """Test that project structure is valid."""  # Triple quotes cause issues
```

**Solution:** Use single quotes and escape when necessary:

```yaml
# ❌ Problematic
def test_project_structure():
    """Test that project structure is valid."""

# ✅ Solution
echo 'def test_project_structure():' > tests/test_basic.py
echo '    assert os.path.exists("README.md"), "README.md should exist"' >> tests/test_basic.py
```

### 3. Heredoc Delimiter Conflicts

**Problem:** Using 'EOF' as heredoc delimiter conflicts with YAML parsing.

**Solution:** 
- Use completely different delimiters (not recommended in YAML)
- **Better:** Avoid heredoc entirely and use echo commands

## Workflow-Specific Solutions

### Python Tests Workflow (`.github/workflows/python-tests.yml`)

**Issues Encountered:**
- Multiple YAML syntax errors (lines 67, 86)
- Heredoc conflicts in test file creation
- Quote parsing issues in Python docstrings

**Final Working Solution:**
```yaml
- name: Create test structure
  run: |
    if [ -d tests ] && [ "$(ls -A tests 2>/dev/null)" ]; then
      echo "Tests directory exists and contains files"
    else
      echo "No tests directory or tests found - creating test structure"
      mkdir -p tests
      echo "# 3dPot test placeholder" > tests/__init__.py
      
      # Create basic tests using echo commands
      echo 'import os' > tests/test_basic.py
      echo '' >> tests/test_basic.py
      echo 'def test_project_structure():' >> tests/test_basic.py
      echo '    assert os.path.exists("README.md"), "README.md should exist"' >> tests/test_basic.py
      echo '    ' >> tests/test_basic.py
      echo 'def test_arduino_codes():' >> tests/test_basic.py
      echo '    assert os.path.exists("codigos/arduino"), "Arduino codes directory should exist"' >> tests/test_basic.py
      echo '    ' >> tests/test_basic.py
      echo 'def test_esp32_codes():' >> tests/test_basic.py
      echo '    assert os.path.exists("codigos/esp32"), "ESP32 codes directory should exist"' >> tests/test_basic.py
      echo '    ' >> tests/test_basic.py
      echo 'def test_3d_models():' >> tests/test_basic.py
      echo '    assert os.path.exists("modelos-3d"), "3D models directory should exist"' >> tests/test_basic.py
      
      # Run the basic tests
      pytest tests/test_basic.py -v --cov=. --cov-report=term-missing
    fi
```

## Best Practices for GitHub Actions YAML

1. **Avoid Heredoc in YAML:** Use sequential `echo` commands instead
2. **Quote Management:** Be careful with nested quotes; prefer single quotes
3. **String Delimiters:** Never use 'EOF' as heredoc delimiter in YAML
4. **Line Length:** Keep multiline strings manageable
5. **Testing:** Test YAML files with online validators before committing

## Validation Tools

- **GitHub Actions YAML Linter:** Built into GitHub interface
- **Online Validators:** yamllint.com, yaml-online-parser.appspot.com
- **Local Validation:** `yamllint .github/workflows/`

## Monitoring Workflow Health

### Check Workflow Status
```bash
# View recent workflow runs
gh run list --limit 10

# View specific workflow status
gh run list --workflow=python-tests.yml --limit 5
```

### Common Workflow Statuses
- **Success:** ✅ All jobs completed successfully
- **Failure:** ❌ One or more jobs failed
- **Cancelled:** Workflow was manually cancelled
- **In Progress:** Currently running

## History of Fixes Applied

| Commit | Issue | Solution |
|--------|-------|----------|
| `2bf4a40` | Quote escaping in docstrings | Fixed quote management |
| `be08f29` | Heredoc delimiter conflict | Changed from 'EOF' to 'PYTEST_EOF' |
| `3329e4d` | Persistent heredoc issues | Simplified to echo commands |
| `175598c` | Final YAML conflict | Completely removed heredoc, used echo-only approach |

## Emergency Troubleshooting Steps

1. **Check YAML Syntax:** Use online YAML validators
2. **Review Recent Changes:** Check commits for recent modifications
3. **Test Locally:** Validate YAML syntax before pushing
4. **Simplify Complex Logic:** Break down complex multiline strings
5. **Use Echo Commands:** For file creation, always prefer echo over heredoc

## Contact

For workflow issues not covered in this guide:
- Check GitHub Actions documentation
- Review workflow logs in the Actions tab
- Create an issue using the bug report template