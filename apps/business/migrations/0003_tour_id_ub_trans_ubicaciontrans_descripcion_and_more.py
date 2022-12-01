# Generated by Django 4.1.3 on 2022-12-01 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_cuentabancaria'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='id_ub_trans',
            field=models.ForeignKey(db_column='id_ub_trans', default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='business.ubicaciontrans'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ubicaciontrans',
            name='descripcion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='ubicaciontrans',
            name='imagen',
            field=models.ImageField(null=True, upload_to='tr_location/'),
        ),
        migrations.AddField(
            model_name='ubicaciontrans',
            name='categoria',
            field=models.CharField(blank=False, max_length=200, null=False),
        ),
    ]