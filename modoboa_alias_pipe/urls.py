from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^alias_pipe/new/$', views.newaliaspipe, name='alias_pipe_add'),
    url(r'^$', views.list, name='list'),
    url(r'^list/$', views._list, name='_list'),
    url(r'^page/$', views._list, name='page'),
    url(r'^(?P<alias_pipe_id>\d+)/edit/$', views.edit, name='alias_pipe_change'),
    url(
        r'^(?P<alias_pipe_id>\d+)/delete/$',
        views.delete,
        name='alias_pipe_delete'),
    url(r'^import/$', views.alias_pipe_import, name="alias_pipe_import"),
]
