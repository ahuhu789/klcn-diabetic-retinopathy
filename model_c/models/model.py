import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class RetinalMultiLabelClassifier(nn.Module):
    """
    Model C: Single-Image Multi-Label Retinal Disease Classifier
    Backbone: Pretrained EfficientNet-B0
    Input: One RGB fundus image (Batch, 3, H, W)
    Output: Raw logits (Batch, num_classes)
    """
    def __init__(self, num_classes=10, pretrained=True, dropout=0.3):
        super().__init__()
        self.num_classes = num_classes
        
        # Load backbone
        weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = efficientnet_b0(weights=weights)
        
        # In_features for EfficientNet-B0 classifier head is 1280
        in_features = self.backbone.classifier[1].in_features
        
        # Custom Multi-label Classification Head
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, num_classes)
        )
        
    def forward(self, x):
        return self.backbone(x)
    
    def predict_proba(self, x):
        """Returns probabilities using sigmoid activation"""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.sigmoid(logits)
            
    def predict(self, x, thresholds=None):
        """Returns binary predictions using provided per-class thresholds or default 0.5"""
        probs = self.predict_proba(x)
        if thresholds is None:
            return (probs >= 0.5).int(), probs
        if isinstance(thresholds, (list, tuple)):
            thresholds = torch.tensor(thresholds, device=x.device).unsqueeze(0)
        return (probs >= thresholds).int(), probs

if __name__ == "__main__":
    model = RetinalMultiLabelClassifier(num_classes=10, pretrained=False)
    dummy_input = torch.randn(2, 3, 224, 224)
    logits = model(dummy_input)
    print("Model test successful!")
    print("Logits shape:", logits.shape)
    assert logits.shape == (2, 10)
