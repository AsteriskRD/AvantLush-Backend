from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0003_alter_product_discount_type'),  
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_type',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_percentage',
            field=models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True),
        ),
    ]