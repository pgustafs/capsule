import cv2
import torch
from torchvision import models, transforms
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import os
from rembg import remove

# Load a pre-trained Faster R-CNN model from torchvision
model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Define a transformation to preprocess the input image
preprocess = transforms.Compose([
    transforms.ToTensor(),
])

def detect_object(image):
    image_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        predictions = model(image_tensor)
    boxes = predictions[0]['boxes'].cpu().numpy()
    scores = predictions[0]['scores'].cpu().numpy()
    if len(scores) > 0:
        max_idx = np.argmax(scores)
        box = boxes[max_idx]
        return box
    return None

def calculate_object_scale(box):
    width = box[2] - box[0]
    height = box[3] - box[1]
    return max(width, height)

def resize_image(image, box, target_scale):
    # Crop the image around the bounding box
    cropped_image = image.crop((box[0], box[1], box[2], box[3]))

    # Calculate the current scale
    current_scale = calculate_object_scale(box)

    # Calculate the resize factor
    resize_factor = target_scale / current_scale

    # Resize the cropped image
    new_size = (int(cropped_image.width * resize_factor), int(cropped_image.height * resize_factor))
    resized_image = cropped_image.resize(new_size, Image.LANCZOS)

    return resized_image

def enhance_image(image):
    # Enhance the image using sharpening
    enhancer = ImageEnhance.Sharpness(image)
    enhanced_image = enhancer.enhance(2.0)  # Increase the sharpness by a factor of 2
    return enhanced_image

def resize_images_to_same_scale(image_paths, target_scale=None, output_size=(224, 224)):
    images = [Image.open(image_path).convert("RGB") for image_path in image_paths]
    boxes = [detect_object(image) for image in images]

    if any(box is None for box in boxes):
        raise ValueError("Object detection failed for one or more images.")

    scales = [calculate_object_scale(box) for box in boxes]
    if target_scale is None:
        target_scale = max(scales)

    resized_images = []
    for image, box in zip(images, boxes):
        resized_image = resize_image(image, box, target_scale)
        
        # Remove background
        resized_image_np = np.array(resized_image)
        no_bg_image = remove(resized_image_np)
        no_bg_image = Image.fromarray(no_bg_image).convert("RGBA")

        enhanced_image = enhance_image(no_bg_image)
        enhanced_image = enhanced_image.resize(output_size, Image.LANCZOS)
        resized_images.append(enhanced_image)

    for idx, (resized_image, image_path) in enumerate(zip(resized_images, image_paths)):
        # Preserve the original file format
        output_path = os.path.splitext(image_path)[0] + f"_resized{os.path.splitext(image_path)[1]}"
        resized_image.save(output_path)

# Example usage
#resize_images_to_same_scale(["shirt.jpg", "shorts.png"])
resize_images_to_same_scale(["images/IMG_8633.png"], target_scale=100)

# images/IMG_8633.png
# images/IMG_8635.png