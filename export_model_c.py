import os
import sys
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
import torch
import torch.nn as nn

# Workspace path setup
workspace_dir = r"c:\Users\thanh\Desktop\klcn"
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from model_c.models.model import RetinalMultiLabelClassifier

class ModelCExportWrapper(nn.Module):
    """Wrapper that outputs probabilities directly via sigmoid"""
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return torch.sigmoid(self.model(x))

def main():
    ckpt_path = os.path.join(workspace_dir, "model_c", "experiments_output", "E2_RFMiD_ODIR_Harmonized_best.pth")
    output_onnx = os.path.join(workspace_dir, "model_c", "experiments_output", "model_c_harmonized.onnx")
    
    print(f"Loading checkpoint from: {ckpt_path}")
    device = torch.device("cpu")
    model = RetinalMultiLabelClassifier(num_classes=10, pretrained=False)
    
    ckpt = torch.load(ckpt_path, map_location=device)
    state_dict = ckpt['model_state_dict'] if 'model_state_dict' in ckpt else ckpt
    model.load_state_dict(state_dict)
    model.eval()
    
    wrapped = ModelCExportWrapper(model)
    wrapped.eval()
    
    dummy_input = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        test_out = wrapped(dummy_input)
    print("PyTorch test inference output shape:", test_out.shape)
    print("Sample probabilities:", test_out.numpy()[0])
    
    print(f"Exporting to single self-contained ONNX at: {output_onnx}...")
    torch.onnx.export(
        wrapped,
        dummy_input,
        output_onnx,
        export_params=True,
        input_names=["input"],
        output_names=["probabilities"],
        dynamic_axes={"input": {0: "batch_size"}, "probabilities": {0: "batch_size"}},
        opset_version=14,
        do_constant_folding=True,
        dynamo=False
    )
    
    print(f"ONNX export completed successfully! File size: {os.path.getsize(output_onnx):,} bytes")

if __name__ == "__main__":
    main()
