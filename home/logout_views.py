"""
Custom logout views to ensure proper redirect
"""
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def custom_logout(request):
    """
    Custom logout view that ALWAYS redirects to login page.
    This prevents the /admin/ redirect issue.
    """
    logout(request)
    return redirect('/accounts/login/')
