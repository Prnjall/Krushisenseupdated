import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
import traceback
import sys

def run_smoke_test():
    print("=== GPU SMOKE TEST ===")
    
    # 1. Check CUDA
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available. GPU training cannot proceed.")
        return False
        
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"PyTorch Version: {torch.__version__}")
    
    device = torch.device('cuda')
    print(f"GPU Model: {torch.cuda.get_device_name(0)}")
    
    # 2. Dataset and Loading Simulation (Using dummy tensors to simulate successful loading)
    # We will simulate the exact tensor sizes that the dataloader would yield.
    try:
        # Simulate batch_size=16, 3 channels, 224x224
        print("Simulating dataset loading...")
        batch_size = 16
        dummy_inputs = torch.randn(batch_size, 3, 224, 224).to(device)
        dummy_labels = torch.randint(0, 16, (batch_size,)).to(device)
        print("Dataset loading simulation successful.")
    except Exception as e:
        print(f"ERROR: Dataset loading simulation failed - {e}")
        traceback.print_exc()
        return False

    # 3. Model Initialization
    try:
        print("Loading MobileNetV3-Small...")
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        num_ftrs = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(num_ftrs, 16)
        model = model.to(device)
        model.train()
        print("Model loaded successfully.")
    except Exception as e:
        print(f"ERROR: Model initialization failed - {e}")
        traceback.print_exc()
        return False

    # 4. Forward Pass
    try:
        print("Executing forward pass...")
        outputs = model(dummy_inputs)
        if outputs.shape != (batch_size, 16):
            print(f"ERROR: Unexpected output shape {outputs.shape}")
            return False
        print("Forward pass successful.")
    except Exception as e:
        print(f"ERROR: Forward pass failed - {e}")
        traceback.print_exc()
        return False

    # 5. Loss Calculation
    try:
        print("Calculating loss...")
        criterion = nn.CrossEntropyLoss()
        loss = criterion(outputs, dummy_labels)
        print("Loss calculation successful.")
    except Exception as e:
        print(f"ERROR: Loss calculation failed - {e}")
        traceback.print_exc()
        return False

    # 6. Backpropagation
    try:
        print("Executing backpropagation...")
        loss.backward()
        print("Backpropagation successful.")
    except Exception as e:
        print(f"ERROR: Backpropagation failed - {e}")
        traceback.print_exc()
        return False

    # 7. Optimizer Step
    try:
        print("Executing optimizer step...")
        optimizer = optim.AdamW(model.parameters(), lr=1e-3)
        optimizer.step()
        print("Optimizer step successful.")
    except Exception as e:
        print(f"ERROR: Optimizer step failed - {e}")
        traceback.print_exc()
        return False
        
    print(f"Max GPU Memory Allocated: {torch.cuda.max_memory_allocated(0) / 1024**2:.2f} MB")
    print("=== SMOKE TEST PASSED ===")
    return True

if __name__ == "__main__":
    success = run_smoke_test()
    if not success:
        sys.exit(1)
