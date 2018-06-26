# -*- coding: utf-8 -*-

"""AppConfig for modoboa_alias_pipe."""

from __future__ import unicode_literals

from django.apps import AppConfig


class AliasPipeConfig(AppConfig):

    """App configuration."""

    name = "modoboa_alias_pipe"
    verbose_name = "Alias pipe functionality using Postfix"

    def ready(self):
        from . import handlers  # NOQA:F401
