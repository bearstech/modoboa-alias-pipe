modoboa-alias-pipe
==================

Modoboa administration panel extension for manage alias pipe commands.

Status : pre-version, not complete, not stable, don't use in production.


Postfix configuration
---------------------

After ``postfix_maps`` execution :

    $ modoboa-admin.py postfix_maps --dburl mysql.... --extensions ... modoboa-alias-pipe

Append this configuration in ``/etc/postfix/main.cf`` :

    alias_maps = hash:/etc/aliases mysql:/etc/postfix/mysql/sql-aliases-pipe.cf ...
    virtual_alias_maps = mysql:/etc/postfix/mysql/sql-virtual-aliases-pipe.cf ...
