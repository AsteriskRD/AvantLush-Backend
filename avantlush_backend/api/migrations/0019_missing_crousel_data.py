from django.db import migrations, models

def populate_text_field(apps, schema_editor):
    """Populate text field with values from title field for existing records"""
    CarouselItem = apps.get_model('api', 'CarouselItem')
    # For any records that have empty text, set default text
    for item in CarouselItem.objects.all():
        if not item.text:
            item.text = "Banner Advertisement"
            item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_carouselitem_options_and_more'),  # Update this to match your migration number
    ]

    operations = [
        migrations.RunPython(populate_text_field),
    ]