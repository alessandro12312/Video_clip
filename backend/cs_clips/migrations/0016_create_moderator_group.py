from django.db import migrations


def create_moderator_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='moderator')


def remove_moderator_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='moderator').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cs_clips', '0015_prd_alignment'),
    ]

    operations = [
        migrations.RunPython(create_moderator_group, remove_moderator_group),
    ]
