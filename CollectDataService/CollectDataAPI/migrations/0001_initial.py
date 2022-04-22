# Generated by Django 3.2.12 on 2022-04-22 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='WebPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=1024)),
                ('pageStructure', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sessions.session')),
            ],
        ),
        migrations.CreateModel(
            name='WebPageIdentifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pageStructure', models.TextField()),
                ('similarityMethod', models.CharField(choices=[('1', 'LCS'), ('2', 'APTED'), ('3', 'LCS_Optimized'), ('4', 'APTED_Optimized')], default='3', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='WebSite',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='WebPageIdentifierWebPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.DecimalField(decimal_places=2, max_digits=3)),
                ('webPage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.webpage')),
                ('webPageIdentifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.webpageidentifier')),
            ],
        ),
        migrations.AddField(
            model_name='webpageidentifier',
            name='webPages',
            field=models.ManyToManyField(through='CollectDataAPI.WebPageIdentifierWebPage', to='CollectDataAPI.WebPage'),
        ),
        migrations.AddField(
            model_name='webpage',
            name='webSite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.website'),
        ),
        migrations.CreateModel(
            name='SequenceIdentifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.sequence')),
                ('webPageIdentifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.webpageidentifier')),
            ],
        ),
        migrations.AddField(
            model_name='sequence',
            name='webPageIdentifiers',
            field=models.ManyToManyField(through='CollectDataAPI.SequenceIdentifier', to='CollectDataAPI.WebPageIdentifier'),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.URLField(unique=True)),
                ('webSite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CollectDataAPI.website')),
            ],
        ),
    ]
