# capsule/views.py
import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Item, Outfit
from .forms import CategoryForm, ItemForm, OutfitForm, OutfitForm1

def index(request):
    return render(request, 'capsule/index.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'capsule/category_list.html', {'categories': categories})

def item_list(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        items = Item.objects.filter(category=category)
    else:
        items = Item.objects.all()
    return render(request, 'capsule/item_list.html', {'items': items, 'category_id': category_id})

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
            form.save()
            return redirect('category_list')
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