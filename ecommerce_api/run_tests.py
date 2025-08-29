#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([
        'users.tests',
        'products.tests', 
        'orders.tests',
        'cart.tests',
        'inventory.tests',
        'promotions.tests'
    ])
    sys.exit(bool(failures))