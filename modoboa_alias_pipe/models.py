from django.db import models
from django.utils.translation import ugettext_lazy

import reversion

from modoboa_admin.models.domain import Domain
from modoboa_admin.models.base import AdminObject


class AliasPipe(AdminObject):
    address = models.CharField(ugettext_lazy('address'), max_length=254)
    domain = models.ForeignKey(Domain)
    command = models.TextField(blank=False)
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


reversion.register(AliasPipe)
