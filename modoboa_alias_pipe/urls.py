from django.urls import path
from . import views

app_name = 'modoboa_alias_pipe'

urlpatterns = [
    path('', views.list, name='list'),
    path('new/', views.newaliaspipe, name='add'),
    path('list/', views._list, name='_list'),
    path('page/', views._list, name='page'),
    path('<int:alias_pipe_id>/edit/',
         views.edit, name='change'),
    path(
        '<int:alias_pipe_id>/delete/',
        views.delete,
        name='delete'),
    path('import/', views.alias_pipe_import, name="import"),
]
