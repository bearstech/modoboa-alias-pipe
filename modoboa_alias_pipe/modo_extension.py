from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import events
from modoboa_admin import signals
from modoboa.lib.email_utils import split_mailbox
from .models import AliasPipe


@events.observe("AdminMenuDisplay")
def admin_menu(target, user):
    if target != "top_menu":
        return []

    entries = []

    if user.is_superuser:
        entries += [
            {
                "name": "alias_pipe",
                "url": reverse("modoboa_alias_pipe:list"),
                "label": _("Alias commands")
            }
        ]

    return entries


class AdminConsole(ModoExtension):
    name = "modoboa_alias_pipe"
    label = ugettext_lazy("Alias pipe")
    version = "1.0.2"
    description = ugettext_lazy(
        "Console to manage alias pipe command"
    )
    always_active = True
    url = "alias-pipe"


exts_pool.register_extension(AdminConsole)


@receiver(signals.use_external_recipients)
def use_external_recipients_cb(sender, **kwargs):
    localpart, domname = split_mailbox(kwargs['recipients'])
    return (
        AliasPipe.objects.filter(
            address=localpart, domain__name=domname
        ).first() is not None
    )
