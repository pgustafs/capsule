import os
import numpy as np
from PIL import Image, ImageEnhance
import cv2
from rembg import remove
from django.db.models.signals import post_save
from django.dispatch import receiver
from sklearn.cluster import KMeans
from collections import Counter
from .models import Item
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

def crop_transparent_area(image):
    # Convert the image to RGBA if it isn't already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get the bounding box of the non-transparent area
    bbox = image.getbbox()
    
    if bbox:
        # Crop the image to the bounding box
        cropped_image = image.crop(bbox)
        
        # Save the cropped image
        return cropped_image
    else:
        logger.info("The image is completely transparent...")
        
def resize_for_processing(image, target_size=(300, 300)):
    """Resize image to target size while maintaining aspect ratio."""
    logger.info("Resizing image for processing...")
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    return image

#def detect_dominant_color(image):
#    logger.info("Detecting dominant color...")
#    # Resize image to speed up processing
#    image = resize_for_processing(image)
#
#    # Convert image to numpy array
#    image_np = np.array(image)
#
#    # Reshape the image to be a list of pixels
#    if image_np.shape[2] == 4:  # If there's an alpha channel, remove it
#        image_np = image_np[:, :, :3]
#
#    pixels = image_np.reshape((-1, 3))
#
#    # Use KMeans to find the most common colors
#    kmeans = KMeans(n_clusters=3, random_state=0)
#    kmeans.fit(pixels)
#    counter = Counter(kmeans.labels_)
#    dominant_color = kmeans.cluster_centers_[counter.most_common(1)[0][0]]
#
#    return tuple(int(c) for c in dominant_color)
#def detect_dominant_color(image, num_colors):
#    # Reshape the image to be a list of pixels
#    pixels = image.reshape((-1, 3))
#
#    # Apply k-means clustering to find dominant colors
#    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
#    _, labels, centers = cv2.kmeans(pixels.astype(np.float32), num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
#
#    # Convert the RGB values of dominant colors to integers
#    dominant_colors = np.uint8(centers)
#
#     # Get the dominant color in RGB
#    dominant_color_rgb = dominant_colors[0]
#
#    # Convert the dominant color to hex
#    dominant_color_hex = rgb_to_hex(dominant_color_rgb)
#
#    return dominant_color_hex

def detect_dominant_color(image, num_colors):
    # Reshape the image to be a list of pixels
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)


    # Apply k-means clustering to find dominant colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_

    # Convert the RGB values of dominant colors to integers
    dominant_colors = colors.astype(int)

     # Get the dominant color in RGB
    dominant_color_rgb = dominant_colors[2]

    # Convert the dominant color to hex
    dominant_color_hex = rgb_to_hex(dominant_color_rgb)

    return dominant_color_hex


@receiver(post_save, sender=Item)
def process_image(sender, instance, **kwargs):
    if instance.image and not instance.image_processed:
        logger.info(f"Processing image: {instance.image.path}")
        image_path = instance.image.path
        image = Image.open(image_path).convert("RGBA")

        # Remove background
        logger.info("Removing background...")
        transparent_image = remove(image)

        # Enhance image
        #logger.info("Enhancing image...")
        #enhancer = ImageEnhance.Sharpness(no_bg_image)
        #enhanced_image = enhancer.enhance(2.0)  # Increase the sharpness by a factor of 2

        # Cropping Image
        cropped_image = crop_transparent_area(transparent_image)

        # Save the processed image
        logger.info("Saving processed image...")
        cropped_image.save(image_path)

        # Detect dominant color
        logger.info("Detecting dominant color...")
        image = cv2.imread(image_path)
        dominant_color = detect_dominant_color(image, 3)
        logger.info(f"Dominant Color: {dominant_color}")

        # Save the dominant color and mark as processed
        instance.dominant_color = dominant_color
        instance.image_processed = True
        instance.save(update_fields=['dominant_color', 'image_processed'])

        logger.info(f"Processing complete for image: {instance.image.path}")