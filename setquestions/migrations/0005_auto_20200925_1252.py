# Generated by Django 3.1.1 on 2020-09-25 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setquestions', '0004_choice_is_checked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='is_checked',
            field=models.CharField(default='unchecked', max_length=100),
        ),
    ]
