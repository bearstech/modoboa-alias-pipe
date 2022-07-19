# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_auto_20151118_1215'),
    ]

    operations = [
        migrations.CreateModel(
            name='AliasPipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=254, verbose_name='address')),
                ('command', models.TextField(help_text='Absolute path to command, example /bin/date')),
                ('enabled', models.BooleanField(default=True, help_text='Check to activate this command', verbose_name='enabled')),
                ('domain', models.ForeignKey(to='admin.Domain', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'alias_pipe',
            },
        ),
    ]
