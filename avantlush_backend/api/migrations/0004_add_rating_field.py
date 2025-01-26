from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0003_tag_product_categories_alter_product_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
    ]
