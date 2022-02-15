from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Credit

@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'phone_number',
        'email',
    ]
    def credit(self,user):
        credit = Credit.objects.get(user=user)
      
        return credit.credit
    

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'credit',
        'expiration_date'
    ]
    
    def __str__(self):
       return self.user
