# Generated by Django 4.1.3 on 2022-12-04 03:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocIdentidad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(default='ACTIVO', max_length=15)),
                ('creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('descripcion', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Documento de Identidad',
                'verbose_name_plural': 'Documentos de Identidad',
                'db_table': 'doc_identidad',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(default='ACTIVO', max_length=15)),
                ('creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('descripcion', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Genero',
                'verbose_name_plural': 'Generos',
                'db_table': 'genero',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(default='ACTIVO', max_length=15)),
                ('creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('run', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('dv', models.CharField(blank=True, max_length=1, null=True)),
                ('pasaporte', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('nombre', models.CharField(max_length=50)),
                ('snombre', models.CharField(blank=True, max_length=50, null=True)),
                ('ap_paterno', models.CharField(max_length=50)),
                ('ap_materno', models.CharField(max_length=50)),
                ('fecha_nacimiento', models.DateField()),
                ('telefono', models.CharField(max_length=20)),
                ('num_calle', models.CharField(max_length=10)),
                ('calle', models.CharField(max_length=30)),
                ('id_ciu', models.IntegerField()),
                ('id_est', models.IntegerField()),
                ('id_pai', models.IntegerField()),
                ('id_doc', models.ForeignKey(db_column='id_doc', on_delete=django.db.models.deletion.DO_NOTHING, to='people.docidentidad')),
                ('id_est1', models.ForeignKey(db_column='id_est1', on_delete=django.db.models.deletion.DO_NOTHING, to='base.estadocivil')),
                ('id_gen', models.ForeignKey(db_column='id_gen', on_delete=django.db.models.deletion.DO_NOTHING, to='people.genero')),
            ],
            options={
                'verbose_name': 'Persona',
                'verbose_name_plural': 'Personas',
                'db_table': 'persona',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Acompaniante',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='people.persona')),
            ],
            options={
                'verbose_name': 'Acompañante',
                'verbose_name_plural': 'Acompañantes',
                'db_table': 'acompaniante',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='people.persona')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'db_table': 'cliente',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='people.persona')),
                ('sueldo', models.IntegerField()),
                ('fecha_contrato', models.DateField()),
                ('id_car', models.ForeignKey(db_column='id_car', on_delete=django.db.models.deletion.DO_NOTHING, to='base.cargo')),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
                'db_table': 'empleado',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Recepcionista',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='people.empleado')),
            ],
            options={
                'verbose_name': 'Recepcionista',
                'verbose_name_plural': 'Recepcionistas',
                'db_table': 'recepcionista',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Conductor',
            fields=[
                ('id', models.OneToOneField(db_column='id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='people.empleado')),
                ('id_veh', models.OneToOneField(db_column='id_veh', on_delete=django.db.models.deletion.DO_NOTHING, to='base.vehiculo')),
            ],
            options={
                'verbose_name': 'Conductor',
                'verbose_name_plural': 'Conductores',
                'db_table': 'conductor',
                'ordering': ['id'],
                'managed': True,
            },
        ),
    ]
