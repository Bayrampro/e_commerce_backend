from django.contrib import admin
from core.models import AllProducts, Category, VerificationCode, CustomUser


class AllProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']


admin.site.register(AllProducts, AllProductAdmin)

admin.site.register(Category)

admin.site.register(VerificationCode)

admin.site.register(CustomUser)

