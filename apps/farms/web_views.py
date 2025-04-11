from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Farm, Field
from .forms import FarmForm, FieldForm  # You'll need to create these forms

@login_required
def farm_list(request):
    farms = Farm.objects.filter(user=request.user)
    return render(request, 'farms/farm_list.html', {'farms': farms})

@login_required
def farm_create(request):
    if request.method == 'POST':
        form = FarmForm(request.POST, request.FILES)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.user = request.user
            farm.save()
            messages.success(request, 'Farm created successfully!')
            return redirect('farms:detail', pk=farm.pk)
    else:
        form = FarmForm()
    
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Create Farm'})

@login_required
def farm_detail(request, pk):
    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    fields = Field.objects.filter(farm=farm)
    return render(request, 'farms/farm_detail.html', {'farm': farm, 'fields': fields})

@login_required
def farm_edit(request, pk):
    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, request.FILES, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Farm updated successfully!')
            return redirect('farms:detail', pk=farm.pk)
    else:
        form = FarmForm(instance=farm)
    
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Edit Farm'})

@login_required
def farm_delete(request, pk):
    farm = get_object_or_404(Farm, pk=pk, user=request.user)
    
    if request.method == 'POST':
        farm.delete()
        messages.success(request, 'Farm deleted successfully!')
        return redirect('farms:list')
    
    return render(request, 'farms/farm_confirm_delete.html', {'farm': farm})

# Field views
@login_required
def field_list(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, user=request.user)
    fields = Field.objects.filter(farm=farm)
    return render(request, 'farms/field_list.html', {'farm': farm, 'fields': fields})

@login_required
def field_create(request, farm_id):
    farm = get_object_or_404(Farm, pk=farm_id, user=request.user)
    
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.farm = farm
            field.save()
            messages.success(request, 'Field created successfully!')
            return redirect('farms:field_detail', pk=field.pk)
    else:
        form = FieldForm()
    
    return render(request, 'farms/field_form.html', {'form': form, 'farm': farm, 'title': 'Create Field'})

@login_required
def field_detail(request, pk):
    field = get_object_or_404(Field, pk=pk, farm__user=request.user)
    return render(request, 'farms/field_detail.html', {'field': field})

@login_required
def field_edit(request, pk):
    field = get_object_or_404(Field, pk=pk, farm__user=request.user)
    
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, 'Field updated successfully!')
            return redirect('farms:field_detail', pk=field.pk)
    else:
        form = FieldForm(instance=field)
    
    return render(request, 'farms/field_form.html', {'form': form, 'field': field, 'title': 'Edit Field'})

@login_required
def field_delete(request, pk):
    field = get_object_or_404(Field, pk=pk, farm__user=request.user)
    farm_id = field.farm.id
    
    if request.method == 'POST':
        field.delete()
        messages.success(request, 'Field deleted successfully!')
        return redirect('farms:field_list', farm_id=farm_id)
    
    return render(request, 'farms/field_confirm_delete.html', {'field': field})