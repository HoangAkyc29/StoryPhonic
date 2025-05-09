from django.db import models
from .user import User
 
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # Thêm các trường đặc biệt cho admin nếu cần
    def __str__(self):
        return f"Admin: {self.user.email}" 