import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import io

def load_model():

    model = AutoModelForImageClassification.from_pretrained('model')
    model.eval()

    processor = AutoImageProcessor.from_pretrained('model')

    return model, processor

model, processor = load_model()

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    inputs = processor(images=image, return_tensors="pt")
    return inputs

def predict(image_bytes):
    inputs = preprocess_image(image_bytes)
    
    # Hacer la predicción sin calcular gradientes
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits if hasattr(outputs, 'logits') else outputs
        predicted_label = logits.argmax(-1).item()
    
    return model.config.id2label[predicted_label]

