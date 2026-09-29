import json
from django.test import TestCase, Client
from django.urls import reverse
from predictions.models import KVK
import uuid

class KVKApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('list_kvks')
        self.nearest_url = reverse('nearest_kvk')

        # Create complete KVK
        self.kvk1 = KVK.objects.create(
            name="KVK Pune II",
            state="Maharashtra",
            district="Pune",
            latitude=18.5204,
            longitude=73.8567,
            has_soil_testing=True,
            soil_testing_price_min=100.00,
            is_active=True
        )

        # Create missing optional fields KVK
        self.kvk2 = KVK.objects.create(
            name="KVK Nashik",
            state="Maharashtra",
            district="Nashik",
            # missing lat/long
            is_active=True
        )

        # Multiple KVKs same district
        self.kvk3 = KVK.objects.create(
            name="KVK Pune I",
            state="Maharashtra",
            district="Pune",
            latitude=19.1,
            longitude=73.9,
            is_active=True
        )

        # Different state
        self.kvk4 = KVK.objects.create(
            name="KVK Bhopal",
            state="Madhya Pradesh",
            district="Bhopal",
            latitude=23.2599,
            longitude=77.4126,
            is_active=True
        )

        # Inactive KVK
        self.kvk_inactive = KVK.objects.create(
            name="KVK Old",
            state="Gujarat",
            district="Surat",
            latitude=21.1702,
            longitude=72.8311,
            is_active=False
        )

    def test_create_kvk(self):
        """1 & 2. Create complete KVK and KVK with missing optional fields"""
        self.assertEqual(KVK.objects.count(), 5)
        self.assertIsNotNone(self.kvk1.id)
        self.assertIsNone(self.kvk2.latitude)

    def test_multiple_kvks_same_district(self):
        """3. Multiple KVKs can belong to the same district"""
        pune_kvks = KVK.objects.filter(district="Pune")
        self.assertEqual(pune_kvks.count(), 2)

    def test_state_filtering(self):
        """4. State filtering"""
        response = self.client.get(self.list_url, {'state': 'Maharashtra'})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 3)
        # Combined filtering
        response = self.client.get(self.list_url, {'state': 'Maharashtra', 'search': 'Pune'})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)

    def test_district_filtering(self):
        """5. District filtering"""
        response = self.client.get(self.list_url, {'district': 'Pune'})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)

    def test_search_by_name(self):
        """6. Search by KVK name"""
        response = self.client.get(self.list_url, {'search': 'Bhopal'})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'KVK Bhopal')

    def test_search_by_district(self):
        """7. Search by district"""
        response = self.client.get(self.list_url, {'search': 'Nashik'})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['district'], 'Nashik')

    def test_pagination(self):
        """8. Pagination limits and edge cases"""
        response = self.client.get(self.list_url, {'limit': 2, 'page': 1})
        data = json.loads(response.content)
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['pagination']['limit'], 2)
        
        response2 = self.client.get(self.list_url, {'limit': 2, 'page': 2})
        data2 = json.loads(response2.content)
        self.assertEqual(len(data2['data']), 2)

        # Invalid cases
        resp = self.client.get(self.list_url, {'page': 0})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.list_url, {'page': -1})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.list_url, {'page': 'abc'})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.list_url, {'limit': 0})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.list_url, {'limit': -1})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.list_url, {'limit': 'abc'})
        self.assertEqual(resp.status_code, 400)
        
        # Limit > allowed returns limited to 100 but doesn't fail
        resp = self.client.get(self.list_url, {'limit': 150})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['pagination']['limit'], 100)

    def test_missing_coordinates(self):
        """9. Missing coordinates are allowed"""
        self.assertIsNone(self.kvk2.latitude)
        self.assertIsNone(self.kvk2.longitude)

    def test_nearest_ignores_missing_coordinates(self):
        """10. Nearest endpoint ignores KVKs without coordinates"""
        response = self.client.get(self.nearest_url, {'latitude': 19.0, 'longitude': 73.8})
        data = json.loads(response.content)
        # kvk2 (Nashik) has no coords, should not be in results
        names = [k['name'] for k in data['data']]
        self.assertNotIn("KVK Nashik", names)

    def test_nearest_ordering(self):
        """11. Nearest endpoint orders by actual distance"""
        # Near Pune I (19.1, 73.9)
        response = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9})
        data = json.loads(response.content)
        self.assertEqual(data['data'][0]['name'], "KVK Pune I")
        self.assertLess(data['data'][0]['distance_km'], 1.0) # Should be ~0
        # Check ascending order
        if len(data['data']) > 1:
            self.assertLessEqual(data['data'][0]['distance_km'], data['data'][1]['distance_km'])

    def test_invalid_latitude_and_boundaries(self):
        """12. Invalid latitude is rejected and boundaries tested"""
        # Boundaries
        resp = self.client.get(self.nearest_url, {'latitude': 90, 'longitude': 73.9})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(self.nearest_url, {'latitude': -90, 'longitude': 73.9})
        self.assertEqual(resp.status_code, 200)
        
        # Out of bounds
        response = self.client.get(self.nearest_url, {'latitude': 91, 'longitude': 73.9})
        self.assertEqual(response.status_code, 400)
        response = self.client.get(self.nearest_url, {'latitude': -91, 'longitude': 73.9})
        self.assertEqual(response.status_code, 400)
        
        response2 = self.client.get(self.nearest_url, {'latitude': 'abc', 'longitude': 73.9})
        self.assertEqual(response2.status_code, 400)
        
        # Missing
        response3 = self.client.get(self.nearest_url, {'longitude': 73.9})
        self.assertEqual(response3.status_code, 400)

    def test_invalid_longitude_and_boundaries(self):
        """13. Invalid longitude is rejected and boundaries tested"""
        # Boundaries
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 180})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': -180})
        self.assertEqual(resp.status_code, 200)
        
        # Out of bounds
        response = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 181})
        self.assertEqual(response.status_code, 400)
        response = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': -181})
        self.assertEqual(response.status_code, 400)

    def test_nearest_limits(self):
        """Test nearest endpoint limits"""
        # Valid limits
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9, 'limit': 1})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['data']), 1)
        
        # Invalid limits
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9, 'limit': 0})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9, 'limit': -1})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9, 'limit': 'abc'})
        self.assertEqual(resp.status_code, 400)
        
        # Limit > maximum should not 500
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9, 'limit': 100})
        self.assertEqual(resp.status_code, 200)

    def test_inactive_excluded_from_nearest(self):
        """14. Inactive KVKs are excluded from nearest results"""
        # Near Surat (21.1702, 72.8311)
        response = self.client.get(self.nearest_url, {'latitude': 21.1702, 'longitude': 72.8311})
        data = json.loads(response.content)
        names = [k['name'] for k in data['data']]
        self.assertNotIn("KVK Old", names)

    def test_nullable_service_fields(self):
        """15. Nullable service fields correctly preserve UNKNOWN"""
        response = self.client.get(self.list_url, {'search': 'Nashik'})
        data = json.loads(response.content)
        services = data['data'][0]['services']
        self.assertIsNone(services['has_soil_testing'])
        self.assertIsNone(services['has_mobile_lab'])
        self.assertIsNone(services['offers_expert_consultation'])

    def test_nullable_pricing(self):
        """16. Pricing remains nullable"""
        response = self.client.get(self.list_url, {'search': 'Nashik'})
        data = json.loads(response.content)
        services = data['data'][0]['services']
        self.assertIsNone(services['soil_testing_price_min'])
        self.assertIsNone(services['soil_testing_price_max'])

    def test_api_response_does_not_fabricate(self):
        """17. API response does not fabricate missing information"""
        response = self.client.get(self.list_url, {'search': 'Nashik'})
        data = json.loads(response.content)
        kvk = data['data'][0]
        self.assertIsNone(kvk['latitude'])
        self.assertIsNone(kvk['longitude'])
        self.assertIsNone(kvk['phone'])
        self.assertIsNone(kvk['email'])
        self.assertIsNone(kvk['website'])
        self.assertIsNone(kvk['address'])
        self.assertNotIn('provenance', kvk) # Provenance removed from public API

    def test_empty_database_and_edge_cases(self):
        """Test edge cases with empty database or only inactive"""
        KVK.objects.all().delete()
        
        # Empty DB Nearest
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['data']), 0)
        
        # Empty DB List
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['data']), 0)
        
        # Only KVKs without coordinates
        KVK.objects.create(name="NoCoord", state="S", district="D", is_active=True)
        resp = self.client.get(self.nearest_url, {'latitude': 19.1, 'longitude': 73.9})
        data = json.loads(resp.content)
        self.assertEqual(len(data['data']), 0)
        
        # Same coordinates
        KVK.objects.create(name="Coord1", state="S", district="D", latitude=10.0, longitude=10.0, is_active=True)
        KVK.objects.create(name="Coord2", state="S", district="D", latitude=10.0, longitude=10.0, is_active=True)
        resp = self.client.get(self.nearest_url, {'latitude': 10.0, 'longitude': 10.0})
        data = json.loads(resp.content)
        self.assertEqual(len(data['data']), 2)
