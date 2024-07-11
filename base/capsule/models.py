# capsule/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

class Item(models.Model):
    SIZE_CHOICES = [
        ('XS', 'X-Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'X-Large'),
    ]

    SEASON_CHOICES = [
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('all year', 'All Year'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField(max_length=100)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    location = models.CharField(max_length=50, null=True, blank=True)
    season = models.CharField(max_length=8, null=True, blank=True, choices=SEASON_CHOICES)
    notes = models.CharField(max_length=500, null=True, blank=True)
    red = models.IntegerField(null=True, blank=True) # RGB Color red
    green = models.IntegerField(null=True, blank=True) # RGB color green
    blue = models.IntegerField(null=True, blank=True) # RGB Color blue
    primary_dominant_color = models.CharField(max_length=7, null=True, blank=True) # HEX value automatically detected from image
    secondary_dominant_color = models.CharField(max_length=7, null=True, blank=True)
    complementary_primary_dominant_color = models.CharField(max_length=7, null=True, blank=True)
    complementary_secondary_dominant_color = models.CharField(max_length=7, null=True, blank=True)
    monochromatic_color_1 = models.CharField(max_length=7, null=True, blank=True)
    monochromatic_color_2 = models.CharField(max_length=7, null=True, blank=True)
    monochromatic_color_3 = models.CharField(max_length=7, null=True, blank=True)
    analogous_color_1 = models.CharField(max_length=7, null=True, blank=True)
    analogous_color_2 = models.CharField(max_length=7, null=True, blank=True)
    image = models.ImageField(upload_to='items/')
    image_processed = models.BooleanField(default=False)  # Track if the image has been processed

    def __str__(self):
        return self.name

class Outfit(models.Model):
    name = models.CharField(max_length=100)
    items = models.ManyToManyField(Item)

    def __str__(self):
        return self.name