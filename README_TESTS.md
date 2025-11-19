# Test Suite for AgriPath Django Project

## Overview
Comprehensive test suite covering models, views, forms, utilities, and integration tests for the AgriPath agricultural AI assistant.

## Test Structure
```
tests/
├── __init__.py
├── test_models.py      # Model tests (Profile)
├── test_views.py       # View tests (Core, Accounts, Home)
├── test_forms.py       # Form validation tests
├── test_utils.py       # API utility function tests
└── test_integration.py # End-to-end integration tests
```

## Running Tests

### Using Django Test Runner
```bash
# Run all tests
python manage.py test tests

# Run specific test module
python manage.py test tests.test_models

# Run with verbose output
python manage.py test tests --verbosity=2

# Run specific test class
python manage.py test tests.test_views.CoreViewsTest
```

### Using Custom Test Runner
```bash
# Run all tests
python run_tests.py

# Run specific test module
python run_tests.py tests.test_models
```

### Using Batch File
```bash
# Run all tests with verbose output
test.bat
```

## Test Coverage

### Models (test_models.py)
- ✅ Profile model creation and signals
- ✅ Profile field validation
- ✅ String representation methods

### Views (test_views.py)
- ✅ Authentication requirements
- ✅ Core AI chat functionality
- ✅ Weather query processing
- ✅ OTP authentication flow
- ✅ Profile management
- ✅ Government policies page

### Forms (test_forms.py)
- ✅ Phone number validation
- ✅ OTP form validation
- ✅ Profile edit form validation
- ✅ Form save functionality

### Utilities (test_utils.py)
- ✅ Gemini AI API integration
- ✅ Weather API integration
- ✅ Error handling for API failures
- ✅ Response post-processing

### Integration (test_integration.py)
- ✅ Complete user authentication flow
- ✅ AI chat session management
- ✅ Weather page with API calls
- ✅ Policies page with AI generation
- ✅ Error handling across components

## Test Features

### Mocking
- External API calls (Gemini, OpenWeather, Twilio)
- Database operations for faster tests
- File uploads and media handling

### Fixtures
- Test users with complete/incomplete profiles
- Authenticated clients
- Mock API responses

### Test Data
- Valid/invalid phone numbers
- Sample weather data
- Mock AI responses in Hindi
- Government policy data

## Environment Setup

### Test Settings
- In-memory SQLite database
- Disabled migrations for speed
- Mock API keys
- Simplified password hashing

### Dependencies
```bash
pip install -r requirements.txt
pip install -r test_requirements.txt
```

## Best Practices

### Test Organization
- One test class per model/view
- Descriptive test method names
- Setup and teardown in setUp/tearDown methods

### Assertions
- Use specific assertions (assertEqual, assertContains)
- Test both success and failure cases
- Verify error messages and status codes

### Mocking
- Mock external dependencies
- Use patch decorators for clean mocking
- Verify mock calls when necessary

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure DJANGO_SETTINGS_MODULE is set
2. **Database Errors**: Use test settings with in-memory DB
3. **API Mocking**: Verify patch paths match actual imports
4. **Session Tests**: Use Django test client for session handling

### Debug Tips
- Use `pytest -s` to see print statements
- Add `import pdb; pdb.set_trace()` for debugging
- Check test database isolation with `--reuse-db`