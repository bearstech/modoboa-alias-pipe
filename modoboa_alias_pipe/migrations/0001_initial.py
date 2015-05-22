# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modoboa_admin', '0002_rename_content_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='AliasPipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=254, verbose_name='address')),
                ('command', models.TextField()),
                ('enabled', models.BooleanField(default=True, help_text='Check to activate this command', verbose_name='enabled')),
                ('dates', models.ForeignKey(to='modoboa_admin.ObjectDates')),
                ('domain', models.ForeignKey(to='modoboa_admin.Domain')),
            ],
            options={
                'db_table': 'alias_pipe',
            },
            bases=(models.Model,),
        ),
    ]
