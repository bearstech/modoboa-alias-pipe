from django.db import IntegrityError
from modoboa.lib.exceptions import Conflict

from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.core.urlresolvers import reverse
import reversion

from modoboa.lib.web_utils import render_to_json_response
from .forms import AliasPipeForm


def _validate_alias(request, form, successmsg, callback=None):
    if form.is_valid():
        form.set_recipients()
        try:
            alias = form.save()
        except IntegrityError:
            raise Conflict(_("Alias with this name already exists"))
        if callback:
            callback(request.user, alias)
        return render_to_json_response(successmsg)

    return render_to_json_response({'form_errors': form.errors}, status=400)


@login_required
@user_passes_test(lambda u: u.is_superuser)
@reversion.create_revision()
def newaliaspipe(request):
    if request.method == "POST":
        def callback(user, alias):
            alias.post_create(user)

        form = AliasPipeForm(request.user, request.POST)
        return _validate_alias(
            request, form, 'Alias pipe created', callback
        )

    return render(
        request,
        "modoboa_alias_pipe/aliaspipeform.html",
        {
            "title": _("New alias pipe"),
            "action": reverse("modoboa_alias_pipe:alias_pipe_add"),
            "formid": "aliaspipeform",
            "action_label": _("Create"),
            "action_classes": "submit",
            "form": AliasPipeForm(request.user)
        }
    )
