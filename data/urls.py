# from debug_toolbar import APP_NAME
from django.urls import path, reverse_lazy, include
from . import views
from django.views.generic import TemplateView
from django.conf import settings 
from django.conf.urls.static import static
# from .views import data_plot_view, data_plot_json  # Временно отключено

app_name='data'
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.UserListView.as_view(), name='user_profile_list'),
    path('create', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/delete', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/update', views.UserUpdateView.as_view(), name='user_update'),
    
    path('users/<int:user_pk>/obj_create', views.ObjCreateView.as_view(), name='obj_create'),
    path('users/<int:user_pk>/obj_detail/<int:pk>', views.ObjDetailView.as_view(), name='obj_detail'),
    path('users/<int:user_pk>/obj_update/<int:pk>', views.ObjUpdateView.as_view(), name='obj_update'),
    path('users/<int:user_pk>/obj_delete/<int:pk>', views.ObjDeleteView.as_view(), name='obj_delete'),
    path('users/<int:user_pk>/obj_list', views.ObjListView.as_view(), name='obj_list'),
    
    path ('users/<int:user_pk>/<int:obj_pk>/sys_create', views.SystemCreateView.as_view(), name='sys_create'),
    path ('users/<int:user_pk>/obj_detail/<int:obj_pk>/sys_detail/<int:pk>', views.SystemDetailView.as_view(), name='sys_detail'),
    path ('users/<int:user_pk>/obj_detail/<int:obj_pk>/sys_update/<int:pk>', views.SystemUpdateView.as_view(), name='sys_update'),
    path ('users/<int:user_pk>/<int:obj_pk>/sys_delete/<int:pk>', views.SystemDeleteView.as_view(), name='sys_delete'),
    
    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_create', views.AtribCreateView.as_view(), name='atr_create'),
    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_detail/<int:pk>', views.AtributeDetailView.as_view(), name='atr_detail'),
    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_detail/', views.AtributeListView.as_view(), name='atr_list'),
    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_update/<int:pk>', views.AtribUpdateView.as_view(), name='atr_update'),
    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_delete/<int:pk>', views.AtibuteDeleteView.as_view(), name='atr_delete'), 

    # path('get_all_carel_vars/<int:sys_pk>', views.get_all_carel_vars, name='get_all_carel_vars'),  # Временно отключено

    path ('users/<int:user_pk>/<int:obj_pk>/<int:sys_pk>/atr_detail/<int:atr_pk>/create_data', views.CreateDataView.as_view(), name='data_create'),

    # path('plot', data_plot_view, name='data_plot'),
    # path('plot/json/', data_plot_json, name='data_plot_json'),
    # path ('users/<int:user_pk>/obj_detail/<int:obj_pk>/sys_detail/<int:sys_pk>/data_plot', data_plot_view, name='data_plot_user'), 
    # path ('users/<int:user_pk>/obj_detail/<int:obj_pk>/sys_detail/<int:sys_pk>/data_plot/json', data_plot_json, name='data_plot_user_json'), 

]
