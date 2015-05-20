from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.core.extensions import ModoExtension, exts_pool
from modoboa.lib import events


@events.observe("ExtraIdentitiesMenuEntries")
def extra_identities_menu_entries(user):
    if user.is_superuser:
        return [
            {"name": "newaliaspipe",
             "label": _("Add alias pipe"),
             "img": "fa fa-plus",
             "url": reverse("modoboa_alias_pipe:alias_pipe_add"),
             "modal": True,
             "modalcb": "alias_pipe_add"}
        ]
    else:
        return []


@events.observe("GetStaticContent")
def get_static_content(caller, st_type, user):
    if (caller == 'identities') and (st_type == 'js'):
        return (
            '<script type="text/javascript" src="/sitestatic/modoboa_alias_pipe/js/admin.js"></script>',  # NOQA
        )


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
