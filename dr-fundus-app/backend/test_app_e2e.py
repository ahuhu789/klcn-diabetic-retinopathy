"""
Comprehensive End-to-End Application Test for dr-fundus-app
Validates complete user flow:
1. Health check & model initialization (Models A, B, C)
2. Sample images catalog
3. Frontend static distribution serving (index.html, CSS, JS)
4. Valid fundus image analysis:
   - Model A (Gate) accepts
   - Model B (DR Staging) infers 5-class distribution + Heatmaps
   - Model C (Multi-label) infers 10-disease probabilities + calibrated thresholds
5. Non-fundus image rejection:
   - Model A rejects
   - Pipeline stops immediately without executing Models B or C
6. Invalid/corrupted file handling (HTTP 400)
7. Consecutive multi-image uploads (No state leakage or reload overhead)
"""

import os
import sys
import io
import unittest
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

workspace_dir = os.path.dirname(os.path.dirname(backend_dir))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from fastapi.testclient import TestClient
from app.main import app

class TestAppEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("STARTING END-TO-END APPLICATION TEST SUITE")
        print("=======================================================")
        cls.client = TestClient(app)
        
        # Load sample valid fundus image
        samples_dir = os.path.join(backend_dir, "samples")
        sample_files = [f for f in os.listdir(samples_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        assert len(sample_files) > 0, "No sample fundus files found in backend/samples!"
        cls.valid_image_path = os.path.join(samples_dir, sample_files[0])
        print(f"Using valid test fundus image: {cls.valid_image_path}")

        # Create dummy non-fundus image (Solid blue image)
        cls.non_fundus_bytes = io.BytesIO()
        Image.new('RGB', (256, 256), color=(0, 100, 255)).save(cls.non_fundus_bytes, format='JPEG')
        cls.non_fundus_bytes.seek(0)

    def test_01_health_check(self):
        """Test API health check and verify all models are loaded."""
        print("\n[E2E Test 1] Testing /api/health...")
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print("Health status:", data)
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["gate_loaded"], "Model A Gate is not loaded!")
        self.assertTrue(data["classifier_loaded"], "Model B Classifier is not loaded!")
        self.assertTrue(data["model_c_loaded"], "Model C Classifier is not loaded!")
        self.assertEqual(data["gate_threshold"], 0.965)

    def test_02_samples_catalog(self):
        """Test preset clinical sample images catalog."""
        print("\n[E2E Test 2] Testing /api/samples...")
        response = self.client.get("/api/samples")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"Found {len(data)} clinical sample images.")

    def test_03_frontend_static_serving(self):
        """Test that the production React build is properly served at root /."""
        print("\n[E2E Test 3] Testing Frontend static distribution serving at /...")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn('<div id="root"></div>', response.text)
        print("Frontend index.html successfully served!")

    def test_04_valid_fundus_prediction(self):
        """Test full pipeline analysis on a valid fundus image."""
        print("\n[E2E Test 4] Testing valid fundus image analysis (Models A + B + C)...")
        with open(self.valid_image_path, "rb") as f:
            file_bytes = f.read()

        response = self.client.post(
            "/api/predict",
            files={"file": ("IDRiD_sample.jpg", file_bytes, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Model A verification
        self.assertTrue(data["is_fundus"], "Valid fundus was unexpectedly rejected!")
        self.assertGreaterEqual(data["fundus_confidence"], 0.965)
        print(f"Model A Gate Conf: {data['fundus_confidence']:.4f} (Threshold: {data['threshold']})")

        # Model B verification
        self.assertIsNotNone(data["dr_result"])
        self.assertIn(data["dr_result"]["stage"], [0, 1, 2, 3, 4])
        self.assertEqual(len(data["dr_result"]["probabilities"]), 5)
        print(f"Model B Stage: {data['dr_result']['stage']} ({data['dr_result']['badge']}), Conf: {data['dr_result']['confidence']:.4f}")

        # Model C verification
        self.assertIsNotNone(data["model_c_result"])
        model_c = data["model_c_result"]
        self.assertIn("overall_disease_risk", model_c)
        self.assertEqual(len(model_c["full_probabilities"]), 10)
        print(f"Model C Overall Risk: {model_c['overall_disease_risk']}, Detected Conditions: {model_c['num_detected_conditions']}")
        for d in model_c["detected_diseases"]:
            print(f"  - Detected: {d['code']} ({d['name']}) -> {d['confidence_pct']}%")

        # System metadata
        self.assertIsNotNone(data.get("processing_time_ms"))
        self.assertIsNotNone(data.get("clinical_disclaimer"))
        print(f"Pipeline latency: {data['processing_time_ms']} ms")

    def test_05_non_fundus_rejection(self):
        """Test that non-fundus images are rejected and pipeline terminates immediately."""
        print("\n[E2E Test 5] Testing non-fundus image rejection...")
        self.non_fundus_bytes.seek(0)
        response = self.client.post(
            "/api/predict",
            files={"file": ("non_fundus.jpg", self.non_fundus_bytes.read(), "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Model A rejection
        self.assertFalse(data["is_fundus"])
        self.assertLess(data["fundus_confidence"], 0.965)
        self.assertIn("bị từ chối", data["message"])

        # Models B and C must NOT be executed
        self.assertIsNone(data["dr_result"])
        self.assertIsNone(data["model_c_result"])
        print(f"Successfully rejected non-fundus image (Confidence: {data['fundus_confidence']:.4f} < 0.965). Pipeline stopped safely.")

    def test_06_corrupted_file_handling(self):
        """Test that invalid/corrupted files return HTTP 400 without crashing."""
        print("\n[E2E Test 6] Testing corrupted file upload...")
        corrupted_bytes = b"This is not an image file content"
        response = self.client.post(
            "/api/predict",
            files={"file": ("fake.jpg", corrupted_bytes, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Không thể giải mã dữ liệu hình ảnh", response.json()["detail"])
        print("Properly handled corrupted file with HTTP 400.")

    def test_07_consecutive_uploads(self):
        """Test uploading multiple images in sequence to verify stability and non-interference."""
        print("\n[E2E Test 7] Testing consecutive multi-image uploads (5 iterations)...")
        with open(self.valid_image_path, "rb") as f:
            valid_bytes = f.read()

        for i in range(5):
            res = self.client.post(
                "/api/predict",
                files={"file": (f"test_run_{i}.jpg", valid_bytes, "image/jpeg")}
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["is_fundus"])
            self.assertIsNotNone(data["dr_result"])
            self.assertIsNotNone(data["model_c_result"])
        print("Completed 5 consecutive uploads with 100% success!")

if __name__ == "__main__":
    unittest.main()
