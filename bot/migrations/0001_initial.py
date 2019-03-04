# Generated by Django 2.1.7 on 2019-03-03 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_1', models.CharField(max_length=100)),
                ('address_2', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('region', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('region_code', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('delay', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15)),
                ('shipping_address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.Address')),
            ],
        ),
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=60)),
                ('number', models.CharField(max_length=16)),
                ('cvv', models.CharField(max_length=5)),
                ('expiry_month', models.CharField(max_length=2)),
                ('expiry_year', models.CharField(max_length=4)),
                ('billing_address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('site_url', models.URLField()),
                ('keywords', models.TextField()),
                ('variant', models.CharField(max_length=30)),
                ('random', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='bot',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.Buyer'),
        ),
        migrations.AddField(
            model_name='bot',
            name='credit_card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.CreditCard'),
        ),
        migrations.AddField(
            model_name='bot',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.Product'),
        ),
    ]