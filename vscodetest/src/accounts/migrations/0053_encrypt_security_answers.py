from django.db import migrations, models
from django.contrib.auth.hashers import make_password


def hash_security_answers(apps, schema_editor):
    """
    Loops through the users and tries to determine if security answer resembles the hashed value.
    If checks pass for a plain text value, hash the value and save it.
    hash example: pbkdf2_sha256$150000$w7aKpc3gOZ1g$zWDAJ2OJrkhXosuKISCfLU9o04cXIjFwcqlFZyUDwVA=
    """

    UserProfile = apps.get_model('accounts', 'UserProfile')

    for user in UserProfile.objects.all():
        hash_needed = False

        # First check to make sure the answer isn't blank
        if not user.password_reset_answer:
            pass   # No hash needed

        # The pbkdf2 hash has a lot more than 18 characters, but 18 is a safe minimum
        elif len(user.password_reset_answer) < 18:
            hash_needed = True

        # Maybe someone's answer is long, so check to make sure it has 3 dollar signs (delimiter)
        elif user.password_reset_answer.count("$") < 3:
            hash_needed = True

        # Finally check if the name of the hashing algorithm is in the answer
        elif not ("pbkdf2_sha256$" in user.password_reset_answer):
            hash_needed = True

        if hash_needed:
            user.password_reset_answer = make_password(user.password_reset_answer)
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0052_auto_20200526_0144'),
    ]

    operations = [
        migrations.RunPython(hash_security_answers, migrations.RunPython.noop),
    ]
