from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserRole(models.Model):    
    description = models.CharField('Descripción',max_length=50, blank=False, null=False,unique=True)

    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuario"
        db_table = 'AUTH_USER_ROLE'

    def __str__(self):
        return self.description


# Create Custom User Manager
class CustomUserManager(BaseUserManager):
    def _create_user(self,email,password,first_name,last_name,middle_name,surname,**extra_fields):
        if not email:
            raise ValueError("No se ha entregado un correo electrónico")

        if not password:
            raise ValueError("No se ha entregado una contraseña")

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            middle_name = middle_name,
            surname = surname,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_user(self, email, password, first_name, last_name, middle_name = None, surname = None, **extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_active' ,True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email, password, first_name, last_name,middle_name, surname, password, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, middle_name = None, surname = None, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, password, first_name, last_name,middle_name, surname, **extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    # Abstractbaseuser has password, last_login, is_active by default
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=240)
    surname = models.CharField(max_length=240)
    image = models.ImageField('Imagen de perfil', upload_to='perfil/', default='', max_length=255, null=True, blank = True)
    role = models.ForeignKey(UserRole, on_delete = models.CASCADE, verbose_name = 'Rol Usuario', null = True)

    is_staff = models.BooleanField(default=True) # must needed, otherwise
    is_active = models.BooleanField(default=True) # must needed, otherwise
    is_superuser = models.BooleanField(default=False) # this field we inherit

    objects = CustomUserManager() 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'surname']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'AUTH_USER_ACCOUNT'