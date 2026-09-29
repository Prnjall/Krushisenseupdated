import pytest
from django.core.management import call_command
from predictions.models import KVK
import sys
import os

# Add the data directory so we can import the script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'kvk')))
from import_kvk import run_import

@pytest.mark.django_db
def test_import_kvk_empty_db():
    assert KVK.objects.count() == 0
    run_import(force=False)
    assert KVK.objects.count() == 726

@pytest.mark.django_db
def test_import_kvk_populated_db_no_force():
    KVK.objects.create(official_id="TEST-1", name="Test KVK", state="Maharashtra")
    assert KVK.objects.count() == 1
    
    # Should skip because force=False
    run_import(force=False)
    assert KVK.objects.count() == 1

@pytest.mark.django_db
def test_import_kvk_populated_db_with_force():
    KVK.objects.create(official_id="TEST-1", name="Test KVK", state="Maharashtra")
    assert KVK.objects.count() == 1
    
    # Should overwrite because force=True
    run_import(force=True)
    assert KVK.objects.count() == 726
    # Ensure our dummy record is gone
    assert not KVK.objects.filter(official_id="TEST-1").exists()
