# Generated by Django 5.1.6 on 2025-02-21 13:19

import cloudinary.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_product_main_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariation',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='price_adjustment',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='productvariation',
            name='sku',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productvariation',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='productvariation',
            unique_together={('product', 'variation_type', 'variation')},
        ),
        migrations.CreateModel(
            name='ProductVariantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('is_primary', models.BooleanField(default=False)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.productvariation')),
            ],
            options={
                'ordering': ['-is_primary', 'id'],
            },
        ),
    ]
