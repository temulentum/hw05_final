# Generated by Django 2.2.16 on 2022-03-01 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0003_auto_20220201_0157"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="posts/", verbose_name="Картинка"
            ),
        ),
    ]
