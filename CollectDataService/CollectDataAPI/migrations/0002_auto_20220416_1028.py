# Generated by Django 3.2.12 on 2022-04-16 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CollectDataAPI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webpage',
            name='pageStructure',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='webpageidentifier',
            name='pageStructure',
            field=models.TextField(),
        ),
    ]
