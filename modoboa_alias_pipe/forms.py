from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.lib.exceptions import BadRequest
from modoboa.lib.form_utils import DynamicForm
from modoboa.lib.email_utils import split_mailbox
from modoboa_admin.models import Domain, Alias


class AliasPipeForm(forms.ModelForm, DynamicForm):
    email = forms.EmailField(
        label=ugettext_lazy("Email address"),
        help_text=ugettext_lazy(
            "The distribution list address. Use the '*' character to create a "
            "'catchall' address (ex: *@domain.tld)."
        ),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    recipients = forms.EmailField(
        label=ugettext_lazy("Recipients"), required=False,
        help_text=ugettext_lazy(
            "Mailbox(es) this alias will point to. Indicate only one address "
            "per input, press ENTER to add a new input."
        ),
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Alias
        fields = ("enabled",)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AliasPipeForm, self).__init__(*args, **kwargs)

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

            if not v.startswith('|'):
                raise BadRequest(
                    u"%s %s" % (_("Invalid pipe command, command need to start with \"|\" character"), v)  # NOQA
                )

            self.ext_rcpts += [v]
            total += 1

        if total == 0:
            raise BadRequest(_("No recipient defined"))

    def save(self, commit=True):
        alias = super(AliasPipeForm, self).save(commit=False)
        local_part, domname = split_mailbox(self.cleaned_data["email"])
        alias.address = local_part
        alias.domain = Domain.objects.get(name=domname)
        if commit:
            alias.save(ext_rcpts=self.ext_rcpts)
            self.save_m2m()

        return alias
