
from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    CustomUser = apps.get_model('api', 'CustomUser')
    for row in CustomUser.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),  # replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),  # temporarily nullable
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='customuser',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]