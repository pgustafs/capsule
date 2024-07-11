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

def preprocess_image(image):
    # Convert image to RGBA if it is not already
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    
    # Print shape after conversion
    print(f"Image shape after conversion: {image.shape}")

    # Filter out transparent pixels
    non_transparent_pixels = image[image[:, :, 3] != 0]
    pixels = non_transparent_pixels[:, :3]  # Drop the alpha channel
    
    # Print shape after filtering transparent pixels
    print(f"Pixels shape after filtering: {pixels.shape}")
    
    return np.float32(pixels)

def get_dominant_colors(pixels, k=3):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    counts = np.bincount(labels)
    dominant_color_indices = np.argsort(counts)[::-1]  # Indices of colors sorted by count in descending order
    return colors.astype(int), dominant_color_indices

def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])  # Convert RGB to Hex

def get_complementary_color(color):
    # Calculate the complementary color
    comp_color = 255 - color
    return comp_color

def get_monochromatic_colors(color):
    # Generate three monochromatic colors: one dark shade, one light tint, and one in the middle
    hsv_color = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
    
    # Dark shade
    dark_shade = np.copy(hsv_color)
    dark_shade[2] = max(0, hsv_color[2] - 50)
    dark_shade_rgb = cv2.cvtColor(np.uint8([[dark_shade]]), cv2.COLOR_HSV2RGB)[0][0]
    
    # Light tint
    light_tint = np.copy(hsv_color)
    light_tint[2] = min(255, hsv_color[2] + 50)
    light_tint_rgb = cv2.cvtColor(np.uint8([[light_tint]]), cv2.COLOR_HSV2RGB)[0][0]
    
    # Middle color (slight adjustment)
    middle_color = np.copy(hsv_color)
    middle_color[2] = min(255, max(0, hsv_color[2]))
    middle_color_rgb = cv2.cvtColor(np.uint8([[middle_color]]), cv2.COLOR_HSV2RGB)[0][0]
    
    return [dark_shade_rgb, middle_color_rgb, light_tint_rgb]

def get_analogous_colors(color):
    # Generate two analogous colors by shifting the hue by ±30 degrees
    hsv_color = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
    analogous_colors = []
    
    # Shift hue by -30 degrees
    analogous_color1 = np.copy(hsv_color)
    analogous_color1[0] = (hsv_color[0] - 30) % 180  # OpenCV uses hue range [0, 180]
    analogous_color1_rgb = cv2.cvtColor(np.uint8([[analogous_color1]]), cv2.COLOR_HSV2RGB)[0][0]
    analogous_colors.append(analogous_color1_rgb)
    
    # Shift hue by +30 degrees
    analogous_color2 = np.copy(hsv_color)
    analogous_color2[0] = (hsv_color[0] + 30) % 180  # OpenCV uses hue range [0, 180]
    analogous_color2_rgb = cv2.cvtColor(np.uint8([[analogous_color2]]), cv2.COLOR_HSV2RGB)[0][0]
    analogous_colors.append(analogous_color2_rgb)
    
    return analogous_colors

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
        num_colors = 3 # number of dominant colors to detect
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)  # Ensure it is in RGBA
        preprocessed_image = preprocess_image(image)
        dominant_colors, dominant_color_indices = get_dominant_colors(preprocessed_image, k=num_colors)
        primary_dominant_color_hex = rgb_to_hex(dominant_colors[dominant_color_indices[0]])
        logger.info(f"Primary Dominant Color: {primary_dominant_color_hex}")
        secondary_dominant_color_hex = rgb_to_hex(dominant_colors[dominant_color_indices[1]])
        logger.info(f"Secondary Dominant Color: {secondary_dominant_color_hex}")
        red, green, blue = dominant_colors[dominant_color_indices[0]].astype(int) # Split RGB into Red, green and blue
        logger.info(f"RGB Red value: {red}")
        logger.info(f"RGB Green value: {green}")
        logger.info(f"RGB Blue value: {blue}")

        # Get complementary colors
        logger.info("Detecting complementary color...")
        primary_dominant_comp_color = get_complementary_color(dominant_colors[dominant_color_indices[0]])
        secondary_dominant_comp_color = get_complementary_color(dominant_colors[dominant_color_indices[1]])
        primary_dominant_comp_color_hex = rgb_to_hex(primary_dominant_comp_color)
        secondary_dominant_comp_color_hex = rgb_to_hex(secondary_dominant_comp_color)

        # Get monochromatic colors
        logger.info("Detecting monochromatic color...")
        monochromatic_colors = get_monochromatic_colors(dominant_colors[dominant_color_indices[0]])
        # Creating dictionary entries
        monochromatic_colors_dict = {}
        for i, color in enumerate(monochromatic_colors):
            monochromatic_colors_dict[f"monochromatic_color_rgb_{i+1}"] = color
            monochromatic_colors_dict[f"monochromatic_color_hex_{i+1}"] = rgb_to_hex(color)
        # Log the values
        #for i in range(1, len(monochromatic_colors) + 1):
        #    logger.info(f"Monochromatic Color {i} (RGB):", monochromatic_colors_dict[f"monochromatic_color_rgb_{i}"])
        #    logger.info(f"Monochromatic Color {i} (Hex):", monochromatic_colors_dict[f"monochromatic_color_hex_{i}"])
        
        # Get analogous colors
        logger.info("Detecting analogous color...")
        analogous_colors = get_analogous_colors(dominant_colors[dominant_color_indices[0]])
        # Creating dictionary entries
        analogous_colors_dict = {}
        for i, color in enumerate(analogous_colors):
            analogous_colors_dict[f"analogous_color_rgb_{i+1}"] = color
            analogous_colors_dict[f"analogous_color_hex_{i+1}"] = rgb_to_hex(color)
        #for i in range(1, len(analogous_colors) + 1):
        #    logger.info(f"Analogousc Color {i} (RGB):", analogous_colors_dict[f"analogous_color_rgb_{i}"])
        #    logger.info(f"Analogous Color {i} (Hex):", analogous_colors_dict[f"analogous_color_hex_{i}"])
        
        # Save the dominant color and mark as processed
        instance.primary_dominant_color = primary_dominant_color_hex
        instance.secondary_dominant_color = secondary_dominant_color_hex
        instance.complementary_primary_dominant_color = primary_dominant_comp_color_hex
        instance.complementary_secondary_dominant_color = secondary_dominant_comp_color_hex
        instance.monochromatic_color_1 = monochromatic_colors_dict["monochromatic_color_hex_1"]
        instance.monochromatic_color_2 = monochromatic_colors_dict["monochromatic_color_hex_2"]
        instance.monochromatic_color_3 = monochromatic_colors_dict["monochromatic_color_hex_3"]
        instance.analogous_color_1 = analogous_colors_dict["analogous_color_hex_1"]
        instance.analogous_color_2 = analogous_colors_dict["analogous_color_hex_2"]
        instance.image_processed = True
        instance.save(update_fields=[
                                    'primary_dominant_color',
                                    'secondary_dominant_color',
                                    'complementary_primary_dominant_color',
                                    'complementary_secondary_dominant_color',
                                    'monochromatic_color_1',
                                    'monochromatic_color_2',
                                    'monochromatic_color_3',
                                    'analogous_color_1',
                                    'analogous_color_2',
                                    'image_processed'
                                    ]
                                )

        logger.info(f"Processing complete for image: {instance.image.path}")