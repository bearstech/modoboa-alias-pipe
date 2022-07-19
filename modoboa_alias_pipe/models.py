from django.db import models
from django.utils.translation import ugettext as _, ugettext_lazy

from modoboa.admin.models.domain import Domain
from modoboa.admin.models.base import AdminObject
from modoboa.lib.email_utils import split_mailbox
from modoboa.lib.exceptions import (
    PermDeniedException, BadRequest, Conflict
)

try:
    from reversion import register
except ImportError:
    from reversion.revisions import register


class AliasPipe(AdminObject):
    address = models.CharField(ugettext_lazy('address'), max_length=254)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    command = models.TextField(
        help_text=ugettext_lazy("Absolute path to command, example /bin/date"),
        blank=False
    )
    enabled = models.BooleanField(
        ugettext_lazy('enabled'),
        help_text=ugettext_lazy("Check to activate this command"),
        default=True
    )

    class Meta:
        app_label = "modoboa_alias_pipe"
        db_table = "alias_pipe"

    def __unicode__(self):
        return self.full_address

    @property
    def full_address(self):
        return "%s@%s" % (self.address, self.domain.name)

    def from_csv(self, user, row, expected_elements=3):
        if len(row) < expected_elements:
            raise BadRequest(_("Invalid line: %s" % row))

        localpart, domname = split_mailbox(row[0].strip())
        try:
            domain = Domain.objects.get(name=domname)
        except Domain.DoesNotExist:
            raise BadRequest(_("Domain '%s' does not exist" % domname))
        if not user.can_access(domain):
            raise PermDeniedException
        try:
            AliasPipe.objects.get(address=localpart, domain__name=domname)
        except AliasPipe.DoesNotExist:
            pass
        else:
            raise Conflict

        self.address = localpart
        self.domain = domain
        self.enabled = (row[1].strip() in ["True", "1", "yes", "y"])
        self.command = row[2].strip().lstrip('|')
        self.save()

    def to_csv(self, csvwriter):
        csvwriter.writerow([
            '%s@%s' % (self.domain, self.address),
            self.enabled,
            self.command
        ])


register(AliasPipe)
