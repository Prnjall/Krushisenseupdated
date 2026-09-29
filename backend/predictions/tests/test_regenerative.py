import json
from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

from predictions.regenerative import calculate_regenerative_score, apply_regenerative_ranking

class TestRegenerativeModule(TestCase):
    def test_normal_healthy_conditions(self):
        # 1. Normal healthy soil/weather/NDVI
        score, reasons = calculate_regenerative_score(
            crop="wheat",
            soil_context={"N": 100, "rainfall": 200},
            weather_context={"risk_signals": []},
            ndvi_context={"status": "AVAILABLE", "ndvi": 0.5},
            base_probability=0.8
        )
        self.assertEqual(score, 0.0)
        self.assertEqual(len(reasons), 0)

    def test_missing_ndvi(self):
        # 2. Missing NDVI
        score, reasons = calculate_regenerative_score(
            crop="chickpea",
            soil_context={"N": 100, "rainfall": 200},
            weather_context={},
            ndvi_context={"status": "UNAVAILABLE"},
            base_probability=0.8
        )
        self.assertEqual(score, 0.0)
        
    def test_missing_weather(self):
        # 3. Missing weather
        score, reasons = calculate_regenerative_score(
            crop="chickpea",
            soil_context={"N": 100, "rainfall": 200},
            weather_context={},
            ndvi_context={"status": "AVAILABLE", "ndvi": 0.5},
            base_probability=0.8
        )
        self.assertEqual(score, 0.0)
        
    def test_missing_soil_field(self):
        # 4. Missing soil field (e.g. N)
        score, reasons = calculate_regenerative_score(
            crop="chickpea",
            soil_context={"rainfall": 200},
            weather_context={},
            ndvi_context={"status": "AVAILABLE", "ndvi": 0.5},
            base_probability=0.8
        )
        self.assertEqual(score, 0.0)

    def test_low_nitrogen_signal(self):
        # 5. Low nitrogen signal
        score, reasons = calculate_regenerative_score(
            crop="chickpea",  # Legume
            soil_context={"N": 20, "rainfall": 200},
            weather_context={},
            ndvi_context={},
            base_probability=0.8
        )
        self.assertTrue(score > 0.0)
        self.assertTrue(any("Legumes fix atmospheric nitrogen" in r for r in reasons))

        score2, reasons2 = calculate_regenerative_score(
            crop="rice",  # Water intensive
            soil_context={"N": 20, "rainfall": 200},
            weather_context={},
            ndvi_context={},
            base_probability=0.8
        )
        self.assertTrue(score2 < 0.0)

    def test_ph_imbalance(self):
        # 6. pH imbalance (not explicitly mapped yet, but ensuring no crash)
        score, reasons = calculate_regenerative_score(
            crop="wheat",
            soil_context={"N": 100, "pH": 4.0, "rainfall": 200},
            weather_context={},
            ndvi_context={},
            base_probability=0.8
        )
        self.assertEqual(score, 0.0)
        
    def test_water_rainfall_risk(self):
        # 7. Water/rainfall risk
        score, reasons = calculate_regenerative_score(
            crop="rice",  # High water demand
            soil_context={"N": 100, "rainfall": 50},  # Low rainfall
            weather_context={"risk_signals": ["Severe dry spell expected"]},
            ndvi_context={},
            base_probability=0.8
        )
        self.assertTrue(score < 0.0)
        self.assertTrue(any("risky" in r for r in reasons))

    def test_apply_ranking(self):
        # 8, 9, 10. Multiple crop candidates, ML ranking baseline, bounded
        base_probs = [
            ("rice", 0.90),
            ("chickpea", 0.85),
            ("wheat", 0.50)
        ]
        results = apply_regenerative_ranking(
            base_probs,
            soil_context={"N": 20, "rainfall": 50},  # Promotes chickpea, penalizes rice
            weather_context={"risk_signals": ["dry spell"]},
            ndvi_context={"status": "AVAILABLE", "ndvi": 0.1} # Low NDVI promotes legume
        )
        
        self.assertEqual(len(results), 3)
        # Chickpea should win because of low N + dry spell + legume NDVI bonus
        self.assertEqual(results[0]["crop"], "chickpea")
        
        # Check bounding (11. No score exceeds valid range)
        for r in results:
            self.assertTrue(-0.15 <= r["regenerative_adjustment"] <= 0.15)
            self.assertTrue(abs(r["final_score"] - r["baseline_probability"]) <= 0.150001)

class TestYieldAndCropFlow(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('predictions.views.yield_prediction_model')
    @patch('predictions.views.crop_recommendation_model')
    def test_predict_crop_flow(self, mock_crop_model, mock_yield_model):
        # 15. Valid yield prediction, 19. Existing crop flow functional
        mock_crop_model.classes_ = ["rice", "chickpea", "wheat"]
        mock_crop_model.predict_proba.return_value = [[0.8, 0.1, 0.1]]
        
        mock_yield_model.predict.return_value = [45.5]
        
        payload = {
            "nitrogen": 100,
            "phosphorus": 50,
            "potassium": 50,
            "temperature": 25,
            "humidity": 60,
            "ph": 6.5,
            "rainfall": 200,
            "weather_current": {"temperature": 25},
            "weather_forecast": {"status": "AVAILABLE", "risk_signals": []},
            "satellite": {"status": "UNAVAILABLE"}
        }
        
        response = self.client.post(
            '/api/predict-crop',
            json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("recommendations", data)
        self.assertIn("estimated_yield", data)
        self.assertEqual(data["estimated_yield"], 45.5)
        self.assertIn("regenerative_ranking", data)
        
    def test_missing_required_input(self):
        # 17. Missing required input
        payload = {
            "nitrogen": 100
            # missing others
        }
        response = self.client.post(
            '/api/predict-crop',
            json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
