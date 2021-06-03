# Generated by Django 3.2.3 on 2021-06-03 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('annotations', '0005_alter_annotation_reviewed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='annotation_reviewer', to='users.user'),
        ),
    ]
