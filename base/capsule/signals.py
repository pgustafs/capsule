import os
from PIL import Image
import pillow_heif
from rembg import remove
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item

def trim_image(image):
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    return image

def make_square(image, size=200):
    x, y = image.size
    max_side = max(x, y)
    new_image = Image.new('RGBA', (max_side, max_side), (255, 255, 255, 0))
    new_image.paste(image, ((max_side - x) // 2, (max_side - y) // 2))
    return new_image

@receiver(post_save, sender=Item)
def process_image(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path

        if instance.image.name.endswith(".HEIC"):
            heif_file = pillow_heif.read_heif(image_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )

        else:
            #image = Image.open(image_path)
            image = Image.open(image_path).convert("RGBA")

        # Remove background
        image = remove(image)

        # Trim the transparent area
        image = trim_image(image)

        # Make the image square by adding transparent padding
        image = make_square(image)

        # Resize the image while keeping aspect ratio
        image.thumbnail((200, 200), Image.LANCZOS)

        # Save the processed image
        image.save(image_path)