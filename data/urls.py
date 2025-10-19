# from debug_toolbar import APP_NAME
from django.conf.urls import url, include
from . import views
from django.views.generic import TemplateView
from django.conf import settings 
from django.conf.urls.static import static
# from .views import data_plot_view, data_plot_json  # Временно отключено

app_name='data'
urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^$', views.UserListView.as_view(), name='user_profile_list'),
    url(r'^create$', views.UserCreateView.as_view(), name='user_create'),
    url(r'^users/(?P<pk>\d+)$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^users/(?P<pk>\d+)/delete$', views.UserDeleteView.as_view(), name='user_delete'),
    url(r'^users/(?P<pk>\d+)/update$', views.UserUpdateView.as_view(), name='user_update'),
    
    url(r'^users/(?P<user_pk>\d+)/obj_create$', views.ObjCreateView.as_view(), name='obj_create'),
    url(r'^users/(?P<user_pk>\d+)/obj_detail/(?P<pk>\d+)$', views.ObjDetailView.as_view(), name='obj_detail'),
    url(r'^users/(?P<user_pk>\d+)/obj_update/(?P<pk>\d+)$', views.ObjUpdateView.as_view(), name='obj_update'),
    url(r'^users/(?P<user_pk>\d+)/obj_delete/(?P<pk>\d+)$', views.ObjDeleteView.as_view(), name='obj_delete'),
    url(r'^users/(?P<user_pk>\d+)/obj_list$', views.ObjListView.as_view(), name='obj_list'),
    
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/sys_create$', views.SystemCreateView.as_view(), name='sys_create'),
    url(r'^users/(?P<user_pk>\d+)/obj_detail/(?P<obj_pk>\d+)/sys_detail/(?P<pk>\d+)$', views.SystemDetailView.as_view(), name='sys_detail'),
    url(r'^users/(?P<user_pk>\d+)/obj_detail/(?P<obj_pk>\d+)/sys_update/(?P<pk>\d+)$', views.SystemUpdateView.as_view(), name='sys_update'),
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/sys_delete/(?P<pk>\d+)$', views.SystemDeleteView.as_view(), name='sys_delete'),
    
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_create$', views.AtribCreateView.as_view(), name='atr_create'),
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_detail/(?P<pk>\d+)$', views.AtributeDetailView.as_view(), name='atr_detail'),
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_detail/$', views.AtributeListView.as_view(), name='atr_list'),
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_update/(?P<pk>\d+)$', views.AtribUpdateView.as_view(), name='atr_update'),
    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_delete/(?P<pk>\d+)$', views.AtibuteDeleteView.as_view(), name='atr_delete'), 

    # url(r'^get_all_carel_vars/(?P<sys_pk>\d+)$', views.get_all_carel_vars, name='get_all_carel_vars'),  # Временно отключено

    url(r'^users/(?P<user_pk>\d+)/(?P<obj_pk>\d+)/(?P<sys_pk>\d+)/atr_detail/(?P<atr_pk>\d+)/create_data$', views.CreateDataView.as_view(), name='data_create'),

    # url(r'^plot$', data_plot_view, name='data_plot'),
    # url(r'^plot/json/$', data_plot_json, name='data_plot_json'),
    # url(r'^users/(?P<user_pk>\d+)/obj_detail/(?P<obj_pk>\d+)/sys_detail/(?P<sys_pk>\d+)/data_plot$', data_plot_view, name='data_plot_user'), 
    # url(r'^users/(?P<user_pk>\d+)/obj_detail/(?P<obj_pk>\d+)/sys_detail/(?P<sys_pk>\d+)/data_plot/json$', data_plot_json, name='data_plot_user_json'), 

]
