# Generated by Django 4.1.3 on 2022-12-17 17:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_alter_shift_day_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facilities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=225)),
                ('facility_id', models.PositiveBigIntegerField(blank=True, default=0, null=True)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('user', models.ManyToManyField(blank=True, related_name='users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'facilities',
            },
        ),
    ]