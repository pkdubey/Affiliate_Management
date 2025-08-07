from django.contrib.auth.models import Group

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    return render(request, 'users/profile_view.html', {'user': request.user})

@login_required
def profile_edit(request):
    # For now, just show a placeholder page
    return render(request, 'users/profile_edit.html', {'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from .forms import UserForm, RoleForm

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin','subadmin']).exists())
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin','subadmin']).exists())
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('users:user_list')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin','subadmin']).exists())
def user_edit(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('users:user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin','subadmin']).exists())
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('users:user_list')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin','subadmin']).exists())
def role_access(request):
    roles = Group.objects.all()
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role updated successfully.')
            return redirect('users:role_access')
    else:
        form = RoleForm()
    return render(request, 'users/role_access.html', {'roles': roles, 'form': form})
