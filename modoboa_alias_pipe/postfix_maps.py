"""Map file definitions for postfix."""

from modoboa.core.commands.postfix_maps import registry


class VirtualAliasesPipeMap(object):
    filename = 'sql-virtual-aliases-pipe.cf'

    mysql = "SELECT concat(ap.address, '-', dom.name, '-pipe') FROM alias_pipe ap INNER JOIN admin_domain dom ON ap.domain_id=dom.id WHERE dom.name='%d' AND dom.enabled=1 AND ap.address='%u' AND ap.enabled=1 LIMIT 1"  # NOQA


class AliasesPipeMap(object):
    filename = 'sql-aliases-pipe.cf'

    mysql = "SELECT concat('|', ap.command) FROM alias_pipe ap INNER JOIN admin_domain dom ON ap.domain_id=dom.id WHERE concat(ap.address, '-', dom.name, '-pipe') = '%s' LIMIT 1"  # NOQA

registry.add_files([VirtualAliasesPipeMap, AliasesPipeMap])
