from django import template
from django.urls import reverse
from modoboa.lib.templatetags.lib_tags import render_link
from modoboa.lib.web_utils import render_actions
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag
def alias_pipe_modifiy_link(alias_pipe):
    return render_link({
        "label": alias_pipe.full_address,
        "modal": True,
        "url": reverse(
            "modoboa_alias_pipe:alias_pipe_change",
            args=[alias_pipe.id]),
        "modalcb": "alias_pipe.alias_pipe_change"
    })


@register.simple_tag
def alias_pipe_actions(alias_pipe):
    return render_actions([
        {
            "name": "delaliaspipe",
            "url": reverse(
                "modoboa_alias_pipe:alias_pipe_delete",
                args=[alias_pipe.id]
            ),
            "img": "fa fa-trash",
            "title": _("Delete %s?" % alias_pipe.full_address),
        }
    ])
