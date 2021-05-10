from django.contrib import admin
from django.db import models
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name','price', 'stock', 'category','modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    list_display_links = ('id', 'product_name', 'price', 'stock')

admin.site.register(Product, ProductAdmin)