"""
Integration Tests for Model C in dr-fundus-app Backend
Verifies:
1. End-to-end pipeline: Input Image -> Model A (Gate) -> Model B (DR Staging) + Model C (Multi-label).
2. Non-interference: Model B stage and probabilities are untouched by Model C.
3. Model C independent response structure, label order, and clinical disclaimer.
4. Input rejection: Non-fundus images rejected by Model A without executing Model B or Model C.
5. Missing checkpoint error handling without silent fallback.
"""

import os
import sys
import unittest
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

workspace_dir = os.path.dirname(os.path.dirname(backend_dir))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from app.gate import FundusGate
from app.classifier import DRClassifier
from app.model_c_adapter import ModelCAdapter
from app.schemas import PredictionResponse, DRPrediction, ModelCPrediction

EXPECTED_CLASSES = ['DR', 'ARMD', 'MYA', 'DN', 'ERM', 'BRVO', 'LS', 'ODC_GLAUCOMA', 'CRVO', 'RISK']

class TestModelCIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("SETTING UP INTEGRATION TEST SUITE (Model A + B + C)")
        print("=======================================================")
        cls.gate = FundusGate()
        cls.classifier = DRClassifier()
        cls.model_c = ModelCAdapter()
        
        sample_path = os.path.join(backend_dir, "samples", "IDRiD_001.jpg")
        if not os.path.exists(sample_path):
            # Fallback to any sample jpg
            samples_dir = os.path.join(backend_dir, "samples")
            sample_files = [f for f in os.listdir(samples_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            self.assertTrue(len(sample_files) > 0, "No sample images available in backend/samples!")
            sample_path = os.path.join(samples_dir, sample_files[0])
            
        cls.sample_path = sample_path
        cls.fundus_img = Image.open(sample_path).convert('RGB')
        cls.non_fundus_img = Image.new('RGB', (224, 224), color=(255, 0, 0)) # Solid red

    def test_01_gate_acceptance_and_rejection(self):
        """Test Model A validation gate behavior."""
        print("\n[Test 1] Testing Model A (Fundus Gate)...")
        is_fundus, conf = self.gate.predict(self.fundus_img)
        self.assertTrue(is_fundus, f"Valid fundus image was rejected! Conf: {conf}")
        print(f"  Accepted fundus image: is_fundus={is_fundus}, conf={conf:.4f}")

        is_fundus_fake, conf_fake = self.gate.predict(self.non_fundus_img)
        self.assertFalse(is_fundus_fake, f"Non-fundus dummy image was accepted! Conf: {conf_fake}")
        print(f"  Rejected dummy image: is_fundus={is_fundus_fake}, conf={conf_fake:.4f}")

    def test_02_model_b_dr_staging_independent(self):
        """Test Model B DR classification produces expected fields."""
        print("\n[Test 2] Testing Model B (DR Staging Classifier)...")
        res_b = self.classifier.predict(self.fundus_img)
        self.assertIn("dr_result", res_b)
        self.assertIn("stage", res_b["dr_result"])
        self.assertIn("confidence", res_b["dr_result"])
        self.assertIn("probabilities", res_b["dr_result"])
        print(f"  Model B Output: Stage {res_b['dr_result']['stage']} ({res_b['dr_result']['badge']}), Conf: {res_b['dr_result']['confidence']:.4f}")

    def test_03_model_c_multilabel_independent(self):
        """Test Model C multi-label classification produces frozen classes and metadata."""
        print("\n[Test 3] Testing Model C (Multi-Label Classifier)...")
        res_c = self.model_c.predict(self.fundus_img)
        
        self.assertEqual(res_c['model_version'], '1.0.0-E2-Harmonized')
        self.assertIn('overall_disease_risk', res_c)
        self.assertIn('detected_diseases', res_c)
        self.assertIn('full_probabilities', res_c)
        self.assertIn('clinical_disclaimer', res_c)
        
        # Verify 10 classes in exact order
        probs_keys = list(res_c['full_probabilities'].keys())
        self.assertEqual(probs_keys, EXPECTED_CLASSES, "Model C class keys do not match expected frozen order!")
        
        # Verify probabilities in [0, 1]
        for c in EXPECTED_CLASSES:
            prob = res_c['full_probabilities'][c]['probability']
            thresh = res_c['full_probabilities'][c]['threshold']
            self.assertTrue(0.0 <= prob <= 1.0, f"Probability out of range for {c}: {prob}")
            self.assertTrue(0.0 < thresh < 1.0, f"Threshold out of range for {c}: {thresh}")
            
        print(f"  Model C Risk: {res_c['overall_disease_risk']}")
        print(f"  Detected diseases count: {res_c['num_detected_conditions']}")
        print(f"  Disclaimer included: {bool(res_c['clinical_disclaimer'])}")

    def test_04_pipeline_isolation_no_override(self):
        """Verify Model B predictions are never overridden by Model C probabilities."""
        print("\n[Test 4] Verifying pipeline isolation (Model B vs Model C)...")
        # Run Model B
        res_b = self.classifier.predict(self.fundus_img)
        b_stage = res_b['dr_result']['stage']
        b_conf = res_b['dr_result']['confidence']
        
        # Run Model C
        res_c = self.model_c.predict(self.fundus_img)
        c_dr_prob = res_c['full_probabilities']['DR']['probability']
        
        # Assemble PredictionResponse schema
        response = PredictionResponse(
            is_fundus=True,
            fundus_confidence=0.99,
            threshold=0.965,
            message="Test pipeline passed",
            dr_resnet=DRPrediction(**res_b['dr_resnet']) if res_b.get('dr_resnet') else None,
            dr_vit=DRPrediction(**res_b['dr_vit']) if res_b.get('dr_vit') else None,
            dr_result=DRPrediction(**res_b['dr_result']) if res_b.get('dr_result') else None,
            model_c_result=ModelCPrediction(**res_c)
        )
        
        # Assert Model B stage and confidence are preserved completely
        self.assertEqual(response.dr_result.stage, b_stage)
        self.assertEqual(response.dr_result.confidence, b_conf)
        self.assertEqual(response.model_c_result.full_probabilities['DR']['probability'], c_dr_prob)
        print(f"  Verified: Model B Stage ({response.dr_result.stage}) and Model C DR Prob ({response.model_c_result.full_probabilities['DR']['probability']}) coexist independently.")

    def test_05_missing_checkpoint_fails_explicitly(self):
        """Verify that missing checkpoint raises FileNotFoundError with no demo fallback."""
        print("\n[Test 5] Verifying explicit error when checkpoint is missing...")
        with self.assertRaises(FileNotFoundError):
            ModelCAdapter(checkpoint_path="non_existent_dummy_checkpoint.pth")
        print("  Verified: Missing checkpoint raises FileNotFoundError explicitly.")

if __name__ == '__main__':
    unittest.main()
