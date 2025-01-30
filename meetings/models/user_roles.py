from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class RoleTypes(models.TextChoices):
        SYSTEM_ADMIN = 'SYSTEM_ADMIN', _('Sistem Yöneticisi')
        MEETING_ADMIN = 'MEETING_ADMIN', _('Toplantı Yöneticisi')
        VISITOR_ADMIN = 'VISITOR_ADMIN', _('Ziyaretçi Yöneticisi')
        STANDARD_USER = 'STANDARD_USER', _('Standart Kullanıcı')

    role = models.CharField(
        max_length=20,
        choices=RoleTypes.choices,
        default=RoleTypes.STANDARD_USER
    )
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class UserPermission(models.Model):
    class PermissionTypes(models.TextChoices):
        CREATE_MEETING = 'CREATE_MEETING', _('Toplantı Oluşturma')
        EDIT_MEETING = 'EDIT_MEETING', _('Toplantı Düzenleme')
        DELETE_MEETING = 'DELETE_MEETING', _('Toplantı Silme')
        VIEW_REPORTS = 'VIEW_REPORTS', _('Raporları Görüntüleme')
        MANAGE_VISITORS = 'MANAGE_VISITORS', _('Ziyaretçi Yönetimi')
        MANAGE_ROOMS = 'MANAGE_ROOMS', _('Oda Yönetimi')
        MANAGE_USERS = 'MANAGE_USERS', _('Kullanıcı Yönetimi')

    role = models.CharField(
        max_length=20,
        choices=CustomUser.RoleTypes.choices
    )
    permission = models.CharField(
        max_length=20,
        choices=PermissionTypes.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['role', 'permission']
        verbose_name = _('Kullanıcı İzni')
        verbose_name_plural = _('Kullanıcı İzinleri')
