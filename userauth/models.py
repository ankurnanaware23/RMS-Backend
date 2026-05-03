from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.

class User(AbstractUser):
    ''' this line removes username completely | but then you have to create a custom user manager too with the help of BaseUserManager
    we are not removing it completely, just not using it for authentication
    currently we are not using username for authentication, but it still exists in the model
    '''
    # username    = None 

    email           = models.EmailField(unique=True) # we have to write this because AbstractUser doesn't have unique email by default
    first_name      = models.CharField(max_length=30, blank=False) # due to this first_name cannot be blank even if admins try to create a new user in the admin panel
    last_name       = models.CharField(max_length=30, blank=False) # due to this last_name cannot be blank even if admins try to create a new user in the admin panel
    otp             = models.CharField(max_length=6, blank=True, null=True) # field to store OTP for verification
    refresh_token   = models.TextField(blank=True, null=True) # store the latest refresh token (rotated on login/refresh)
  
    USERNAME_FIELD = 'email' # Use email to log in
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] # Fields required when creating a superuser

    def __str__(self):
        return self.email
    
# Profile model to store additional user information
class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    phone       = models.CharField(max_length=15, blank=True, null=True)
    address     = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/',default="default-user.jpg", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name} Profile"
        else:
            return f"{self.user.email} Profile"

# Signals to create or update user profile automatically
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save user profile when User instance is saved
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Connecting the signals
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
