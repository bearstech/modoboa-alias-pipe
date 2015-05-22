from django.db import IntegrityError
from modoboa.lib.exceptions import Conflict

from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse
import reversion
from modoboa.lib.listing import get_listing_page
from modoboa.lib.web_utils import _render_to_string, render_to_json_response

from .forms import AliasPipeForm
from .models import AliasPipe


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


@login_required
@user_passes_test(lambda u: u.is_superuser)
@ensure_csrf_cookie
def list(request):
    return render(
        request,
        "modoboa_alias_pipe/list.html",
        {
            "selection": "alias_pipe",
            "deflocation": "list/",
            "add_alias_command_entry": {
                "name": "newaliaspipe",
                "label": _("Add alias pipe"),
                "img": "fa fa-plus",
                "url": reverse("modoboa_alias_pipe:alias_pipe_add"),
                "modal": True,
                "modalcb": "alias_pipe.alias_pipe_add"
            }
        }
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def _list(request):
    # TODO append searchquery implentation
    objects = AliasPipe.objects.select_related()
    page = get_listing_page(objects, request.GET.get("page", 1))

    context = {}
    if page is None:
        context["length"] = 0
    else:
        context["headers"] = _render_to_string(
            request, "modoboa_alias_pipe/alias_pipe_headers.html", {})
        context["rows"] = _render_to_string(
            request, "modoboa_alias_pipe/alias_pipe_table.html", {
                "objects": page.object_list
            }
        )
        context["pages"] = [page.number]

    return render_to_json_response(context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def get_next_page(request):
    pass


@login_required
@user_passes_test(lambda u: u.is_superuser)
@ensure_csrf_cookie
def edit(request, alias_pipe_id):
    alias_pipe = AliasPipe.objects.get(pk=alias_pipe_id)

    ctx = {
        'action': reverse(
            'modoboa_alias_pipe:alias_pipe_change',
            args=[alias_pipe.id]),
        'formid': 'aliaspipeform',
        'title': alias_pipe.full_address,
        'action_label': _('Update'),
        'action_classes': 'submit',
        'form': AliasPipeForm(request.user, instance=alias_pipe)
    }

    if request.method == "POST":
        form = AliasPipeForm(request.user, request.POST, instance=alias_pipe)
        return _validate_alias(request, form, _("Alias pipe command modified"))

    return render(
        request,
        "modoboa_alias_pipe/aliaspipeform.html",
        ctx)


def delete(request):
    pass
