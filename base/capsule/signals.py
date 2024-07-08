import os
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
from django.db.models.signals import post_save
from django.dispatch import receiver
from sklearn.cluster import KMeans
from collections import Counter
from .models import Item
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def resize_for_processing(image, target_size=(300, 300)):
    """Resize image to target size while maintaining aspect ratio."""
    logger.info("Resizing image for processing...")
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    return image

def detect_dominant_color(image):
    logger.info("Detecting dominant color...")
    # Resize image to speed up processing
    image = resize_for_processing(image)

    # Convert image to numpy array
    image_np = np.array(image)

    # Reshape the image to be a list of pixels
    if image_np.shape[2] == 4:  # If there's an alpha channel, remove it
        image_np = image_np[:, :, :3]

    pixels = image_np.reshape((-1, 3))

    # Use KMeans to find the most common colors
    kmeans = KMeans(n_clusters=3, random_state=0)
    kmeans.fit(pixels)
    counter = Counter(kmeans.labels_)
    dominant_color = kmeans.cluster_centers_[counter.most_common(1)[0][0]]

    return tuple(int(c) for c in dominant_color)

@receiver(post_save, sender=Item)
def process_image(sender, instance, **kwargs):
    if instance.image and not instance.image_processed:
        logger.info(f"Processing image: {instance.image.path}")
        image_path = instance.image.path
        image = Image.open(image_path).convert("RGBA")

        # Remove background
        logger.info("Removing background...")
        image_np = np.array(image)
        no_bg_image = remove(image_np)
        no_bg_image = Image.fromarray(no_bg_image).convert("RGBA")

        # Enhance image
        logger.info("Enhancing image...")
        enhancer = ImageEnhance.Sharpness(no_bg_image)
        enhanced_image = enhancer.enhance(2.0)  # Increase the sharpness by a factor of 2

        # Save the processed image
        logger.info("Saving processed image...")
        enhanced_image.save(image_path)

        # Detect dominant color
        dominant_color = detect_dominant_color(enhanced_image)

        # Save the dominant color and mark as processed
        instance.dominant_color = f'#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}'
        instance.image_processed = True
        instance.save(update_fields=['dominant_color', 'image_processed'])

        logger.info(f"Processing complete for image: {instance.image.path}")