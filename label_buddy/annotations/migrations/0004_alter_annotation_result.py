# Generated by Django 3.2.3 on 2021-06-03 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0003_alter_annotation_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='result',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
