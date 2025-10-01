from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserForm, RoleForm
from django.http import JsonResponse
import json

User = get_user_model()

@login_required
def profile_view(request):
    return render(request, 'users/profile_view.html', {'user': request.user})

@login_required
def profile_edit(request):
    return render(request, 'users/profile_edit.html', {'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
@role_required(['admin', 'subadmin'])
def user_list(request):
    users = User.objects.all()
    add_form = UserForm()
    edit_forms = {u.pk: UserForm(instance=u) for u in users}

    return render(
        request,
        "users/user_list.html",
        {
            "users": users,
            "form": add_form,
            "edit_forms": edit_forms
        }
    )

@login_required
@role_required(['admin', 'subadmin'])
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'User created successfully.'
                })
            else:
                # Return form errors as JSON
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
        
        # Fallback for non-AJAX requests
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('users:user_list')
        else:
            users = User.objects.all()
            edit_forms = {u.pk: UserForm(instance=u) for u in users}
            return render(request, 'users/user_list.html', {
                "users": users,
                "form": form,
                "edit_forms": edit_forms,
            })
    else:
        return redirect('users:user_list')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['admin', 'subadmin', 'publisher']).exists())
def user_edit(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'User updated successfully.'
                })
            else:
                # Return form errors as JSON
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })
        
        # Fallback for non-AJAX requests
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('users:user_list')
        else:
            users = User.objects.all()
            edit_forms = {u.pk: UserForm(instance=u) for u in users}
            edit_forms[user.pk] = form
            return render(request, 'users/user_list.html', {
                "users": users,
                "form": UserForm(),
                "edit_forms": edit_forms,
            })
    else:
        return redirect('users:user_list')

@login_required
@role_required(['admin', 'subadmin'])
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('users:user_list')

@login_required
@role_required(['admin', 'subadmin'])
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
