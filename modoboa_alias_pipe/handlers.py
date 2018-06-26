# -*- coding: utf-8 -*-

"""Django signal handlers for modoboa_postfix_autoreply."""

from __future__ import unicode_literals

from django.db.models import signals
from django.dispatch import receiver

from modoboa.core import signals as core_signals

from . import postfix_maps


@receiver(core_signals.register_postfix_maps)
def register_postfix_maps(sender, **kwargs):
    """Register postfix maps."""
    return [
        postfix_maps.VirtualAliasesPipeMap,
        postfix_maps.AliasesPipeMap,
    ]


