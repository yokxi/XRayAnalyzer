import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from PIL import Image
import torchvision.transforms as T

def get_model(num_classes=2):
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)
    
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    
    return model

def load_model(model_path, device):
    model = get_model(num_classes=2)
    
    checkpoint = torch.load(model_path, map_location=device)
    
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
        model.load_state_dict(checkpoint['state_dict'])
    elif isinstance(checkpoint, dict):
        model.load_state_dict(checkpoint)
    else:
        model = checkpoint
        
    model.to(device)
    model.eval()
    return model

def get_prediction(model, image_bytes, device, threshold=0.5):
    transforms = T.Compose([T.ToTensor()])
    img = Image.open(image_bytes).convert("RGB")
    img_tensor = transforms(img).to(device)
    
    with torch.no_grad():
        prediction = model([img_tensor])
    
    pred_boxes = prediction[0]['boxes'].cpu().numpy()
    pred_scores = prediction[0]['scores'].cpu().numpy()
    pred_labels = prediction[0]['labels'].cpu().numpy()
    
    print(f"DEBUG: Raw Scores: {pred_scores}")
    print(f"DEBUG: Raw Labels: {pred_labels}")
    print(f"DEBUG: Raw Boxes: {pred_boxes}")

    valid_indices = pred_scores >= threshold
    boxes = pred_boxes[valid_indices].tolist()
    scores = pred_scores[valid_indices].tolist()
    
    print(f"DEBUG: Filtered Boxes (threshold {threshold}): {boxes}")
    
    return boxes, scores
