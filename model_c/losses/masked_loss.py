import torch
import torch.nn as nn
import torch.nn.functional as F

class MaskedBCEWithLogitsLoss(nn.Module):
    """
    Masked Binary Cross-Entropy with Logits Loss for Multi-Label Learning with Missing Labels.
    
    Handles unverified or missing annotations indicated by mask = 0 (and target = -1).
    Ensures that unverified conditions do not contribute to gradient updates, preventing
    false negative hallucination when integrating heterogeneous datasets.
    """
    def __init__(self, pos_weight=None, reduction="mean"):
        super().__init__()
        self.pos_weight = pos_weight
        self.reduction = reduction

    def forward(self, logits, targets, mask):
        """
        Args:
            logits: (Batch, Num_Classes) raw model outputs
            targets: (Batch, Num_Classes) targets in {-1, 0, 1}
            mask: (Batch, Num_Classes) binary mask in {0, 1}
        Returns:
            scalar loss
        """
        # Ensure mask is float
        mask = mask.float()
        
        # Clamp targets so -1 becomes 0 (masked elements will be multiplied by 0 mask anyway)
        clean_targets = torch.clamp(targets.float(), min=0.0, max=1.0)
        
        # Element-wise BCE with logits
        pos_weight_tensor = self.pos_weight.to(logits.device) if self.pos_weight is not None else None
        bce_unreduced = F.binary_cross_entropy_with_logits(
            logits, clean_targets, pos_weight=pos_weight_tensor, reduction="none"
        )
        
        # Apply mask
        masked_bce = bce_unreduced * mask
        
        if self.reduction == "none":
            return masked_bce
            
        # Normalize by total active annotations across batch
        active_elements = mask.sum().clamp(min=1.0)
        loss = masked_bce.sum() / active_elements
        return loss

if __name__ == "__main__":
    loss_fn = MaskedBCEWithLogitsLoss()
    logits = torch.randn(4, 3)
    # Class 0: verified 1, Class 1: verified 0, Class 2: unverified -1
    targets = torch.tensor([[1.0, 0.0, -1.0], [0.0, 1.0, -1.0], [1.0, 1.0, 0.0], [0.0, 0.0, -1.0]])
    mask = torch.tensor([[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0], [1.0, 1.0, 0.0]])
    loss = loss_fn(logits, targets, mask)
    print("Masked BCE loss computation successful! Loss value:", loss.item())
