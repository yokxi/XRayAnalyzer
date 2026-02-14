import os
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms as T

BATCH_SIZE = 8          
NUM_EPOCHS = 5          
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

print(f"⚙️  Modalità Object Detection attiva su: {DEVICE}")

class PneumoniaDetectionDataset(Dataset):
    def __init__(self, csv_file, img_dir, transforms=None):
        self.csv = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transforms = transforms
        
        # lista di pazienti
        self.image_ids = self.csv['patientId'].unique()

    def __len__(self):
        return len(self.image_ids)

    # viene eseguito per ogni singola immagine.
    def __getitem__(self, idx):
        img_id = self.image_ids[idx]
        img_path = os.path.join(self.img_dir, img_id + ".png")
        
        # Carica immagine
        img = Image.open(img_path).convert("RGB")
        
        # Prende tutte le righe di questo paziente
        records = self.csv[self.csv['patientId'] == img_id]
        
        boxes = []
        labels = []
        
        # Se il target è 1 ci sono coordinate
        for i, row in records.iterrows():
            if row['Target'] == 1:
                # Convertiamo da (x, y, larghezza, altezza) a (x_min, y_min, x_max, y_max)
                x_min = row['x']
                y_min = row['y']
                x_max = row['x'] + row['width']
                y_max = row['y'] + row['height']
                boxes.append([x_min, y_min, x_max, y_max])
                labels.append(1) # 1 = Polmonite

        # Convertiamo in tensori
        if len(boxes) > 0:
            boxes = torch.as_tensor(boxes, dtype=torch.float32)
            labels = torch.as_tensor(labels, dtype=torch.int64)
        else:
            # se è sano deve imparare a non disegnare niente quindi -> 0
            boxes = torch.zeros((0, 4), dtype=torch.float32)
            labels = torch.zeros((0,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["image_id"] = torch.tensor([idx])
        
        # Trasformiamo l'immagine in tensore
        if self.transforms:
            img = self.transforms(img)

        return img, target

def collate_fn(batch):
    return tuple(zip(*batch))

def get_transform():
    return T.Compose([T.ToTensor()])

def get_model_instance_segmentation(num_classes):
    # Faster R-CNN -> modello preaddestrato
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # Sfondo + Polmonite
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    
    return model

# preparazione dei dati
print("📂 Preparazione dati...")
dataset = PneumoniaDetectionDataset(
    csv_file='dataset_preProcessed/stage2_train_metadata.csv',
    img_dir='dataset_preProcessed/Training/Images',
    transforms=get_transform()
)

indices = torch.randperm(len(dataset)).tolist()
dataset_train = torch.utils.data.Subset(dataset, indices[:-1000]) 
dataset_test = torch.utils.data.Subset(dataset, indices[-1000:])  

# porta i dati dal dataset alla gpu
train_loader = DataLoader(
    dataset_train, batch_size=BATCH_SIZE, shuffle=True, 
    num_workers=2, collate_fn=collate_fn 
)

# addestramento
model = get_model_instance_segmentation(num_classes=2) # 2 classi: Sfondo e Malattia
model.to(DEVICE)

params = [p for p in model.parameters() if p.requires_grad]

# metodo chiamato SGD -> per aggiustare i neuroni ogni volta che l'AI sbaglia
optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)

print("Inizio Addestramento Object Detection...")

for epoch in range(NUM_EPOCHS):
    model.train()
    epoch_loss = 0
    
    for i, (images, targets) in enumerate(train_loader):
        images = list(image.to(DEVICE) for image in images)
        targets = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]

        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

        epoch_loss += losses.item()

        if (i+1) % 50 == 0:
            print(f"Epoch {epoch+1}, Step {i+1}, Loss: {losses.item():.4f}")


    print(f"Fine Epoca {epoch+1}. Loss Media: {epoch_loss/len(train_loader):.4f}")
    
    # Salva un file diverso per ogni epoca 
    nome_file = f"modello_detection_epoch_{epoch+1}.pth"
    torch.save(model.state_dict(), nome_file)
    print(f"Salvataggio intermedio: {nome_file}")

print("Addestramento Completato mannaggia la madonna!")
print("Salvataggio modello Object Detection...")
torch.save(model.state_dict(), "modello_detection_polmonite.pth")