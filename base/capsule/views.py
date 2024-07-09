# capsule/views.py
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, SubCategory, Item, Outfit
from .forms import CategoryForm, ItemForm, OutfitForm, OutfitForm1

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'capsule/index.html')

# Sidebar
def category_items(request, category_id):
    category = Category.objects.get(id=category_id)
    items = Item.objects.filter(category=category)
    return render(request, 'capsule/category_items.html', {'category': category, 'items': items})

def subcategory_items(request, subcategory_id):
    subcategory = SubCategory.objects.get(id=subcategory_id)
    items = Item.objects.filter(subcategory=subcategory)
    return render(request, 'capsule/subcategory_items.html', {'subcategory': subcategory, 'items': items})

# Items 

# list all items
def item_list(request, category_sub_id=None):
    if category_sub_id:
        if category_sub_id.startswith('category_'):
            category_id = int(category_sub_id.split('_')[1])
            category = get_object_or_404(Category, id=category_id)
            items = Item.objects.filter(category=category)
        elif category_sub_id.startswith('subcategory_'):
            subcategory_id = int(category_sub_id.split('_')[1])
            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            items = Item.objects.filter(subcategory=subcategory)
    else:
        items = Item.objects.all()

    return render(request, 'capsule/item_list.html', {'items': items})

# Item details
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'capsule/item_detail.html', {'item': item})

# Delete Item
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        logger.info(f"Deleting item: {item_id}")
        item.delete()
        return redirect('item_list_no_category')  # Redirect to item list after deletion
    logger.info(f"Displaying confirmation for deleting item: {item_id}")
    return render(request, 'capsule/item_confirm_delete.html', {'item': item})

def outfit_list(request):
    outfits = Outfit.objects.all()
    return render(request, 'capsule/outfit_list.html', {'outfits': outfits})

def outfit_detail(request, outfit_id):
    outfit = get_object_or_404(Outfit, id=outfit_id)
    return render(request, 'capsule/outfit_detail.html', {'outfit': outfit})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'capsule/add_category.html', {'form': form})

def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            choice = form.cleaned_data['category_or_subcategory']
            if choice.startswith('category_'):
                category_id = int(choice.split('_')[1])
                item.category = Category.objects.get(id=category_id)
                item.subcategory = None
                item.save()
                return redirect('item_list', category_sub_id=f"category_{category_id}")
            elif choice.startswith('subcategory_'):
                subcategory_id = int(choice.split('_')[1])
                item.subcategory = SubCategory.objects.get(id=subcategory_id)
                item.category = None
                item.save()
                return redirect('item_list', category_sub_id=f"subcategory_{subcategory_id}")
    else:
        form = ItemForm()
    return render(request, 'capsule/add_item.html', {'form': form})

def add_outfit(request):
    if request.method == 'POST':
        form = OutfitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('outfit_list')
    else:
        form = OutfitForm()
    return render(request, 'capsule/add_outfit.html', {'form': form})

def create_outfit(request):
    if request.method == 'POST':
        form = OutfitForm1(request.POST)
        if form.is_valid():
            outfit = form.save(commit=False)
            outfit.save()
            item_ids = json.loads(request.POST.get('items', '[]'))
            outfit.items.set(item_ids)
            return redirect('outfit_list')
    else:
        form = OutfitForm1()
    items = Item.objects.all()
    return render(request, 'capsule/create_outfit.html', {'form': form, 'items': items})