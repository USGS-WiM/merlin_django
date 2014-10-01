# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Acid',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=128)),
                ('concentration', models.FloatField(default=-999)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnalysisType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('analysis', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlankWater',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('lot_number', models.CharField(max_length=128)),
                ('concentration', models.FloatField(default=-999)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bottle',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('bottle_unique_name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bromination',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('concentration', models.FloatField()),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConstituentMedium',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConstituentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConstituentType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('constituent', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cooperator',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('agency', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('phone', models.BigIntegerField(null=True, blank=True)),
                ('sec_phone', models.BigIntegerField(null=True, blank=True)),
                ('address', models.CharField(max_length=128, blank=True)),
                ('city', models.CharField(max_length=128, blank=True)),
                ('state', models.CharField(max_length=2, blank=True)),
                ('zipcode', models.BigIntegerField(null=True, blank=True)),
                ('country', models.CharField(max_length=128, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DetectionLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('limit', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldSample',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('time_stamp', models.DateTimeField()),
                ('depth', models.FloatField()),
                ('length', models.FloatField(null=True, blank=True)),
                ('comment', models.TextField(blank=True)),
                ('received_time_stamp', models.DateTimeField()),
                ('login_comment', models.TextField(blank=True)),
                ('replicate', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldSampleBottle',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('tare_weight', models.FloatField()),
                ('volume_filtered', models.FloatField()),
                ('filter_weight', models.FloatField()),
                ('preservation_volume', models.FloatField(null=True, blank=True)),
                ('preservation_comment', models.TextField(blank=True)),
                ('description', models.TextField()),
                ('bottle', models.ForeignKey(to='mercuryservices.Bottle')),
                ('field_sample', models.ForeignKey(to='mercuryservices.FieldSample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldSampleMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('raw_value', models.FloatField()),
                ('reported_value', models.FloatField()),
                ('daily_detection_limit', models.FloatField()),
                ('analyzed_date', models.DateTimeField()),
                ('analysis_comment', models.TextField(blank=True)),
                ('analysis_type', models.ForeignKey(to='mercuryservices.AnalysisType')),
                ('constituent_type', models.ForeignKey(to='mercuryservices.ConstituentType')),
                ('field_sample', models.ForeignKey(to='mercuryservices.FieldSample')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FilterType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('filter', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediumType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('nwis_code', models.CharField(max_length=128, blank=True)),
                ('medium', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MethodType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('method', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreservationType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('preservation', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcedureStatusType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcedureType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('procedure', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=128, blank=True)),
                ('accounting_code', models.CharField(max_length=128, blank=True)),
                ('cooperator', models.ForeignKey(related_name='projects', to='mercuryservices.Cooperator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectSite',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('project', models.ForeignKey(to='mercuryservices.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QualityAssurance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('quality_assurance', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('usgs_sid', models.CharField(max_length=128, blank=True)),
                ('usgs_scode', models.CharField(max_length=128, blank=True)),
                ('description', models.TextField(blank=True)),
                ('latitudedd', models.DecimalField(decimal_places=2, null=True, max_digits=10, blank=True)),
                ('longitudedd', models.DecimalField(decimal_places=3, null=True, max_digits=11, blank=True)),
                ('datum', models.CharField(max_length=128, blank=True)),
                ('method', models.CharField(max_length=128, blank=True)),
                ('site_status', models.CharField(max_length=128, blank=True)),
                ('nwis_customer_code', models.CharField(max_length=128, blank=True)),
                ('projects', models.ManyToManyField(related_name='sites', to='mercuryservices.Project', through='mercuryservices.ProjectSite')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status_id', models.BigIntegerField()),
                ('time_stamp', models.DateTimeField()),
                ('note', models.TextField(blank=True)),
                ('procedure_type', models.ForeignKey(to='mercuryservices.ProcedureType')),
            ],
            options={
                'verbose_name_plural': 'Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status_type', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnitType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('unit', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('initials', models.CharField(max_length=6, blank=True)),
                ('phone', models.BigIntegerField(null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='status',
            name='status_type',
            field=models.ForeignKey(to='mercuryservices.StatusType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='status',
            name='user',
            field=models.ForeignKey(to='mercuryservices.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectsite',
            name='site',
            field=models.ForeignKey(to='mercuryservices.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='procedurestatustype',
            name='procedure_type',
            field=models.ForeignKey(to='mercuryservices.ProcedureType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='procedurestatustype',
            name='status_type',
            field=models.ForeignKey(to='mercuryservices.StatusType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplemethod',
            name='method_type',
            field=models.ForeignKey(to='mercuryservices.MethodType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplemethod',
            name='quality_assurance',
            field=models.ForeignKey(to='mercuryservices.QualityAssurance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplemethod',
            name='unit_type',
            field=models.ForeignKey(to='mercuryservices.UnitType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplebottle',
            name='filter_type',
            field=models.ForeignKey(to='mercuryservices.FilterType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplebottle',
            name='preservation_acid',
            field=models.ForeignKey(to='mercuryservices.Acid'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsamplebottle',
            name='preservation_type',
            field=models.ForeignKey(to='mercuryservices.PreservationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsample',
            name='medium_type',
            field=models.ForeignKey(to='mercuryservices.MediumType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fieldsample',
            name='site',
            field=models.ForeignKey(to='mercuryservices.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constituentmethod',
            name='constituent_type',
            field=models.ForeignKey(to='mercuryservices.ConstituentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constituentmethod',
            name='method_type',
            field=models.ForeignKey(to='mercuryservices.MethodType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constituentmedium',
            name='constituent_type',
            field=models.ForeignKey(to='mercuryservices.ConstituentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constituentmedium',
            name='medium_type',
            field=models.ForeignKey(to='mercuryservices.MediumType'),
            preserve_default=True,
        ),
    ]
