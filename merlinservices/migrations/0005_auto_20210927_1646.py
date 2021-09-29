# Generated by Django 2.2.24 on 2021-09-27 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merlinservices', '0004_auto_20201005_1559'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='QualityAssuranceType',
            new_name='QualityAssuranceFlag',
        ),
        migrations.RenameField(
            model_name='qualityassurance',
            old_name='quality_assurance',
            new_name='quality_assurance_flag',
        ),
        migrations.RenameField(
            model_name='qualityassuranceflag',
            old_name='quality_assurance',
            new_name='quality_assurance_flag',
        ),
        migrations.AlterField(
            model_name='qualityassurance',
            name='result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quality_assurance_flags', to='merlinservices.Result'),
        ),
        migrations.AlterUniqueTogether(
            name='qualityassurance',
            unique_together={('quality_assurance_flag', 'result')},
        ),
        migrations.AlterModelTable(
            name='qualityassuranceflag',
            table='mercury_qualityassuranceflag',
        ),
    ]