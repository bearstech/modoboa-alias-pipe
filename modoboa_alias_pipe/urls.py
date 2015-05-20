from django.conf.urls import patterns, url

urlpatterns = patterns(
    'modoboa_alias_pipe.views',
    url(r'^alias_pipe/new/$', 'newaliaspipe', name="alias_pipe_add"),
)
