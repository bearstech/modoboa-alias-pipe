from django import forms
from django.http import QueryDict
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.lib.exceptions import BadRequest
from modoboa.lib.form_utils import DynamicForm
from modoboa.lib.email_utils import split_mailbox
from modoboa_admin.models import Domain
from modoboa_admin.forms import ImportDataForm

from .models import AliasPipe


class AliasPipeForm(forms.ModelForm, DynamicForm):
    email = forms.EmailField(
        label=ugettext_lazy("Email address"),
        help_text=ugettext_lazy(
            "The distribution list address. Use the '*' character to create a "
            "'catchall' address (ex: *@domain.tld)."
        ),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    recipients = forms.CharField(
        label=ugettext_lazy("Commands"), required=False,
        help_text=ugettext_lazy("Absolute path to command, example /bin/date"),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = AliasPipe
        fields = ("enabled",)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AliasPipeForm, self).__init__(*args, **kwargs)
        if len(args) and isinstance(args[0], QueryDict):
            if "instance" in kwargs:
                if not kwargs["instance"].domain.enabled:
                    del self.fields["enabled"]
            self._load_from_qdict(args[0], "recipients", forms.CharField)
        elif "instance" in kwargs:
            instance = kwargs["instance"]
            self.fields["email"].initial = instance.full_address
            if not instance.domain.enabled:
                self.fields["enabled"].widget.attrs["disabled"] = "disabled"

            cpt = 1
            for addr in instance.command.split(','):
                if addr == "":
                    continue
                name = "recipients_%d" % (cpt)
                self._create_field(forms.CharField, name, addr, 2)
                cpt += 1

    def clean_email(self):
        localpart, domname = split_mailbox(self.cleaned_data["email"])
        try:
            domain = Domain.objects.get(name=domname)
        except Domain.DoesNotExist:
            raise forms.ValidationError(_("Domain does not exist"))
        if not self.user.can_access(domain):
            raise forms.ValidationError(
                _("You don't have access to this domain")
            )
        return self.cleaned_data["email"].lower()

    def set_recipients(self):
        self.ext_rcpts = []
        total = 0

        for k, v in self.cleaned_data.items():
            if not k.startswith("recipients"):
                continue
            if v == "":
                continue

            self.ext_rcpts += [v.strip().lstrip('|')]
            total += 1

        if total == 0:
            raise BadRequest(_("No recipient defined"))

    def save(self, commit=True):
        alias_pipe = super(AliasPipeForm, self).save(commit=False)
        local_part, domname = split_mailbox(self.cleaned_data["email"])
        alias_pipe.address = local_part
        alias_pipe.domain = Domain.objects.get(name=domname)
        alias_pipe.command = ",".join(self.ext_rcpts)
        if commit:
            alias_pipe.save()
            self.save_m2m()

        return alias_pipe


class AliasPipeImportForm(ImportDataForm):
    pass
