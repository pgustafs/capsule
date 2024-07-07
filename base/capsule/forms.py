# capsule/forms.py
from django import forms
from .models import Category, Item, Outfit
import magic

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
    

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'brand', 'size', 'color', 'image']
        widgets = {
            'size': forms.Select(choices=Item.SIZE_CHOICES)
        }

    # Update the Form to Recognize HEIC Images, needs libmagic and python-magic installed 
    # Dont know if this is needed since most browsers dont support it 
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Use python-magic to check the mime type
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(image.read())
            
            # Reset the file pointer to the beginning
            image.seek(0)
            
            # Check if the image is HEIF
            if mime_type not in ['image/heic', 'image/heif']:
                # Allow usual image types as well
                if not mime_type.startswith('image/'):
                    raise forms.ValidationError('File is not a valid image.')
            
        return image

class OutfitForm(forms.ModelForm):
    class Meta:
        model = Outfit
        fields = ['name', 'items']

    def __init__(self, *args, **kwargs):
        super(OutfitForm, self).__init__(*args, **kwargs)
        self.fields['items'].widget = forms.CheckboxSelectMultiple()
        self.fields['items'].queryset = Item.objects.all()

class OutfitForm1(forms.ModelForm):
    class Meta:
        model = Outfit
        #fields = ['name', 'items']
        fields = ['name']
        widgets = {
            'items': forms.CheckboxSelectMultiple()
        }
