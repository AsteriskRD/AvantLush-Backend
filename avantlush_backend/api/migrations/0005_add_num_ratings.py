from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_add_rating_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='num_ratings',
            field=models.IntegerField(default=0),
        ),
    ]