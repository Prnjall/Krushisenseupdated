import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../data/kvk'))
from enrich_coordinates import GeocodingPipeline

class TestGeocodingPipeline:
    def setup_method(self):
        with patch('enrich_coordinates.OPENCAGE_API_KEY', 'dummy_key'):
            self.pipeline = GeocodingPipeline(use_mocks=False, dry_run=False)

    @patch('requests.get')
    def test_high_confidence_result(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": {"code": 200},
            "results": [{
                "confidence": 9,
                "components": {"_type": "village", "state": "Maharashtra", "country": "India"},
                "geometry": {"lat": 18.0, "lng": 74.0}
            }]
        }
        mock_get.return_value = mock_response

        resp = self.pipeline.geocode("Query")
        status, coord, reason = self.pipeline.evaluate_result(resp["results"][0], "Maharashtra")
        assert status == "HIGH_CONFIDENCE"
        assert coord["lat"] == 18.0

    def test_state_mismatch(self):
        result = {
            "confidence": 9,
            "components": {"_type": "village", "state": "Gujarat", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "MANUAL_REVIEW"
        assert coord is None

    def test_unicode_normalization_maharashtra(self):
        result = {
            "confidence": 9,
            "components": {"_type": "village", "state": "Mahārāshtra", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "HIGH_CONFIDENCE"
        assert coord["lat"] == 18.0

    def test_unicode_normalization_bihar(self):
        result = {
            "confidence": 9,
            "components": {"_type": "building", "state": "Bihār", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Bihar")
        assert status == "HIGH_CONFIDENCE"

    def test_unicode_normalization_tamil_nadu(self):
        result = {
            "confidence": 9,
            "components": {"_type": "road", "state": "Tamil Nādu", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Tamil Nadu")
        assert status == "HIGH_CONFIDENCE"

    def test_country_mismatch(self):
        result = {
            "confidence": 10,
            "components": {"_type": "building", "state": "Maharashtra", "country": "USA"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "FAILED"
        assert coord is None

    def test_administrative_centroid(self):
        result = {
            "confidence": 6,
            "components": {"_type": "district", "state": "Maharashtra", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "AMBIGUOUS"
        assert coord is None
        
    def test_broad_city_rejection(self):
        result = {
            "confidence": 7,
            "components": {"_type": "city", "state": "Maharashtra", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "AMBIGUOUS"
        assert coord is None
        
    def test_postcode_rejection(self):
        result = {
            "confidence": 8,
            "components": {"_type": "postcode", "state": "Maharashtra", "country": "India"},
            "geometry": {"lat": 18.0, "lng": 74.0}
        }
        status, coord, reason = self.pipeline.evaluate_result(result, "Maharashtra")
        assert status == "AMBIGUOUS"
        assert coord is None

    def test_empty_provider_response(self):
        status, coord, reason = self.pipeline.evaluate_result({}, "Maharashtra")
        assert status == "FAILED"
        assert coord is None

    @patch('requests.get')
    @patch('time.sleep')
    def test_429_retry(self, mock_sleep, mock_get):
        mock_fail = MagicMock()
        mock_fail.status_code = 429
        
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": {"code": 200}}
        
        mock_get.side_effect = [mock_fail, mock_success]
        
        resp = self.pipeline.geocode("Query")
        assert resp["status"]["code"] == 200
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(2)

    @patch('requests.get')
    @patch('time.sleep')
    def test_503_retry(self, mock_sleep, mock_get):
        mock_fail = MagicMock()
        mock_fail.status_code = 503
        
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": {"code": 200}}
        
        mock_get.side_effect = [mock_fail, mock_fail, mock_success]
        
        resp = self.pipeline.geocode("Query")
        assert resp["status"]["code"] == 200
        assert mock_get.call_count == 3
        mock_sleep.assert_any_call(2)
        mock_sleep.assert_any_call(4)

    @patch('requests.get')
    def test_permanent_400_failure(self, mock_get):
        mock_fail = MagicMock()
        mock_fail.status_code = 400
        mock_fail.json.return_value = {"status": {"code": 400}}
        mock_get.return_value = mock_fail
        
        resp = self.pipeline.geocode("Query")
        assert resp["status"]["code"] == 400
        assert mock_get.call_count == 1
