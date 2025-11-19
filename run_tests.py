#!/usr/bin/env python
"""
Test runner script for the Django AgriPath project
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mypage.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test modules or all tests
    test_modules = sys.argv[1:] if len(sys.argv) > 1 else [
        'tests.test_models',
        'tests.test_forms', 
        'tests.test_views',
        'tests.test_utils',
        'tests.test_integration'
    ]
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        sys.exit(bool(failures))