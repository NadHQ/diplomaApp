# Generated by Django 4.1.3 on 2022-12-12 14:51

import MriSoftware.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MriSoftware", "0006_alter_images_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="images",
            name="image",
            field=models.ImageField(
                max_length=200, upload_to=MriSoftware.models.upload_imageOriginal
            ),
        ),
        migrations.AlterField(
            model_name="images",
            name="masked",
            field=models.ImageField(
                max_length=200, upload_to=MriSoftware.models.upload_imageMasked
            ),
        ),
        migrations.AlterField(
            model_name="research",
            name="file",
            field=models.FileField(
                max_length=200, null=True, upload_to=MriSoftware.models.upload_link
            ),
        ),
    ]
