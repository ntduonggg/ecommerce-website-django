from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'slug', 'price', 'stock', 'category', 'is_available', 'modified_at')
    list_editable = ('price', 'stock', 'is_available')

admin.site.register(Product, ProductAdmin)