from django.conf.urls import patterns, url

urlpatterns = patterns(
    'modoboa_alias_pipe.views',
    url(r'^alias_pipe/new/$', 'newaliaspipe', name='alias_pipe_add'),
    url(r'^$', 'list', name='list'),
    url(r'^list/$', '_list', name='_list'),
    url(r'^page/$', '_list', name='page'),
    url(r'^(?P<alias_pipe_id>\d+)/edit/$', 'edit', name='alias_pipe_change'),
    url(
        r'^(?P<alias_pipe_id>\d+)/delete/$',
        'delete',
        name='alias_pipe_delete')
)
