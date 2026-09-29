import os
import sys
import json
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from predictions.models import KVK
from django.utils import timezone

import argparse

def run_import(force=False):
    if not force and KVK.objects.exists():
        print(f"KVK database already contains {KVK.objects.count()} records. Skipping import.")
        print("To perform a destructive re-import, run with --force.")
        return

    import_path = os.path.join(os.path.dirname(__file__), 'kvk_proposed_import.json')
    enrich_path = os.path.join(os.path.dirname(__file__), 'kvk_coordinate_enrichment.json')
    
    # Load base records
    with open(import_path, 'r', encoding='utf-8') as f:
        base_records = json.load(f)
        
    # Load enrichment data mapped by official_id
    enrich_map = {}
    with open(enrich_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            enrich_map[data['official_id']] = data
            
    print(f"Loaded {len(base_records)} base records and {len(enrich_map)} enrichment records.")
    
    # Process records
    to_create = []
    
    for record in base_records:
        official_id = record['official_id']
        enrich_data = enrich_map.get(official_id)
        
        # Base attributes
        attrs = {
            'name': record.get('name') or "",
            'state': record.get('state') or "",
            'district': record.get('district') or "",
            'atari_zone': record.get('atari_zone'),
            'host_organization': record.get('host_organization'),
            'host_organization_type': record.get('host_organization_type'),
            'address': record.get('address'),
            'phone': record.get('phone'),
            'email': record.get('email'),
            'website': record.get('website'),
            
            'source_name': record.get('source_name'),
            'source_url': record.get('source_url'),
            'source_verified_at': record.get('source_verified_at'),
        }
        
        if attrs['source_verified_at']:
            try:
                attrs['source_verified_at'] = datetime.fromisoformat(attrs['source_verified_at'].replace('Z', '+00:00'))
            except:
                attrs['source_verified_at'] = None
                
        # Apply enrichment if available
        if enrich_data:
            attrs['geocoding_status'] = enrich_data['status']
            
            if enrich_data['status'] == 'HIGH_CONFIDENCE':
                attrs['latitude'] = enrich_data['accepted_lat']
                attrs['longitude'] = enrich_data['accepted_lng']
                attrs['coordinate_accuracy'] = enrich_data['coordinate_accuracy']
                attrs['coordinate_source'] = enrich_data['provider']
                
                try:
                    ts = enrich_data['request_timestamp']
                    if 'T' in ts:
                        attrs['coordinate_verified_at'] = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    else:
                        attrs['coordinate_verified_at'] = timezone.now()
                except:
                    attrs['coordinate_verified_at'] = timezone.now()
            else:
                attrs['latitude'] = None
                attrs['longitude'] = None
                attrs['coordinate_accuracy'] = None
                attrs['coordinate_source'] = None
                attrs['coordinate_verified_at'] = None
                
        kvk = KVK(official_id=official_id, **attrs)
        to_create.append(kvk)
        
    print(f"Creating {len(to_create)} KVK records...")
    
    # Delete existing to replace dataset
    deleted, _ = KVK.objects.all().delete()
    if deleted > 0:
        print(f"Deleted {deleted} existing KVK records.")
    
    KVK.objects.bulk_create(to_create)
    print("Import complete.")
    
    print("\nVerification:")
    print(f"Total in DB: {KVK.objects.count()}")
    print(f"With Coordinates: {KVK.objects.filter(latitude__isnull=False).count()}")
    print(f"HIGH_CONFIDENCE: {KVK.objects.filter(geocoding_status='HIGH_CONFIDENCE').count()}")
    print(f"AMBIGUOUS: {KVK.objects.filter(geocoding_status='AMBIGUOUS').count()}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import KVK records")
    parser.add_argument('--force', action='store_true', help="Force overwrite existing records")
    args = parser.parse_args()
    
    run_import(force=args.force)
