from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='部署名')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manage_departments',
        verbose_name='部長',
    )
    def __str__(self):
        return self.name

class Team(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='teams',
        verbose_name='部署',
    )
    name = models.CharField(max_length=100, verbose_name='課名')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='manage_teams',
        verbose_name='課長',
    )
    def __str__(self):
        return f"{self.department.name if self.department else '未所属'} - {self.name}"

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('employee', '社員'),
        ('manager', '上司'),
        ('hr', '人事'),
    )
    GENDER_CHOICES = (
        ('male', '男性'),
        ('female', '女性'),
        ('other', 'その他'),
        ('no_answer', '回答しない'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    employee_number = models.CharField(max_length=20, unique=True, verbose_name='社員番号')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name='users',
        blank=True,
        null=True,
        verbose_name='所属部署',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name='team_users',
        blank=True,
        null=True,
        verbose_name='所属課',
    )
    full_name = models.CharField(max_length=50, verbose_name='氏名')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='no_answer', verbose_name='性別')

    def __str__(self):
        return f'{self.full_name} ({self.employee_number})'

    @property
    def is_employee(self):
        return self.role == 'employee'
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_hr(self):
        return self.role == 'hr'
    
    def save(self, *args, **kwargs):
        if self.is_hr:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)
