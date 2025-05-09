from django.db import models
from .user import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # Thêm các trường khác nếu cần

    def __str__(self):
        return self.full_name or self.user.email 