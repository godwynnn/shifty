# Generated by Django 4.0.4 on 2022-12-19 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_notes_shared_with_remove_notes_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilities',
            name='location',
            field=models.CharField(blank=True, max_length=225),
        ),
    ]
