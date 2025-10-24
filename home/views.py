"""
Home Views - Главный дашборд ProMonitor
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from data.models import Obj, System, AlertRule, Atributes, Data
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """
    Redirect old dashboard to Dashboard V2
    """
    return redirect('dashboard_v2')



def index(request):
    """
    Главная страница - если авторизован → дашборд, иначе → логин
    """
    if request.user.is_authenticated:
        return dashboard(request)
    else:
        return redirect('login')
