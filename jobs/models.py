from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):  # Custom user model extending AbstractUser
    experience = models.IntegerField()
    designation = models.CharField(max_length=255)
    skills = models.TextField()

    # Resolve conflicts by setting unique related_name values
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="userprofile_users",  # Changed related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="userprofile_permissions",  # Changed related_name
        blank=True
    )

class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    company_pwd = models.CharField(max_length=255)

    class Meta:
        db_table = 'companies' 

class Recommendation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    job_id = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
