import csv

from django.db import IntegrityError
from django.db.models import Q
from django.utils.translation import ugettext as _, ungettext
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import (
    login_required, user_passes_test
)
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.urlresolvers import reverse

from modoboa.lib.email_utils import split_mailbox
from modoboa.lib.exceptions import Conflict
from modoboa.lib.listing import get_listing_page
from modoboa.lib.web_utils import render_to_json_response
from modoboa.lib.exceptions import ModoboaException

from .forms import AliasPipeForm, AliasPipeImportForm
from .models import AliasPipe

try:
    from reversion import create_revision
except ImportError:
    from reversion.revisions import create_revision

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
@create_revision()
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
            },
            "import_entry": {
                "name": "alias_pipe_import",
                "label": _("Import"),
                "img": "fa fa-folder-open",
                "url": reverse("modoboa_alias_pipe:alias_pipe_import"),
                "modal": True,
                "modalcb": "alias_pipe.importform_cb"
            }
        }
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def _list(request):
    q = Q()
    searchquery = request.GET.get('searchquery', None)
    if searchquery:
        local_part, domname = split_mailbox(searchquery)
        if local_part:
            q |= Q(address__icontains=local_part)
        if domname:
            q |= Q(domain__name__icontains=domname)

        q |= Q(command__icontains=searchquery)

    objects = AliasPipe.objects.filter(q).select_related()
    page = get_listing_page(objects, request.GET.get("page", 1))

    context = {}
    if page is None:
        context["length"] = 0
    else:
        context["headers"] = render_to_string(
            "modoboa_alias_pipe/alias_pipe_headers.html", {}, request)
        context["rows"] = render_to_string(
            "modoboa_alias_pipe/alias_pipe_table.html", {
                "objects": page.object_list
            }, request
        )
        context["pages"] = [page.number]

    return render_to_json_response(context)


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


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete(request, alias_pipe_id):
    alias_pipe = AliasPipe.objects.get(pk=alias_pipe_id)
    full_address = alias_pipe.full_address
    alias_pipe.delete()
    return render_to_json_response(
        ungettext(
            "Alias pipe deleted %s" % full_address,
            "Alias pipe deleted %s" % full_address,
            1
        )
    )


def import_alias_pipe(user, row, formopts):
    alias_pipe = AliasPipe()
    alias_pipe.from_csv(user, row)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def alias_pipe_import(request):
    if request.method == "POST":
        error = None
        form = AliasPipeImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                reader = csv.reader(request.FILES['sourcefile'],
                                    delimiter=form.cleaned_data['sepchar'])
            except csv.Error as inst:
                error = str(inst)

            if error is None:
                try:
                    cpt = 0
                    for row in reader:
                        if not row:
                            continue

                        try:
                            import_alias_pipe(
                                request.user, row, form.cleaned_data)
                        except Conflict:
                            if form.cleaned_data["continue_if_exists"]:
                                continue
                            raise Conflict(
                                _("Object already exists: %s"
                                  % form.cleaned_data['sepchar'].join(row[:2]))
                            )
                        cpt += 1

                    return render(request, "modoboa_alias_pipe/import_done.html", {
                        "status": "ok",
                        "msg": _("%d objects imported successfully" % cpt)
                    })
                except (ModoboaException) as e:
                    error = str(e)

        return render(request, "modoboa_alias_pipe/import_done.html", {
            "status": "ko", "msg": error
        })

    helptext = _("""Provide a CSV file where lines respect the following formats:
<ul>
<li><em>address; enabled; |/path/to/command</em></li>
</ul>

<p>You can use a different character as separator.</p>
""")

    return render(
        request,
        "modoboa_alias_pipe/importform.html",
        {
            "title": _("Import alias pipe"),
            "action": reverse("modoboa_alias_pipe:alias_pipe_import"),
            "formid": "aliaspipeimportform",
            "enctype": "multipart/form-data",
            "action_label": _("Import"),
            "action_classes": "submit",
            "target": "import_target",
            "form": AliasPipeImportForm(),
            "helptext": helptext
        }
    )
