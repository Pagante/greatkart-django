from django.contrib import admin
from django.db import models
from .models import Product, Variation, reviewRating

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name','price', 'stock', 'category','modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    list_display_links = ('id', 'product_name', 'price', 'stock')


class VariationAdmin(admin.ModelAdmin):
    list_display  = ('id','product', 'variation_category', 'variation_value' ,'is_active')
    list_display_links = ('id','product', 'variation_category', 'variation_value' )
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value' )

admin.site.register(Product, ProductAdmin)

admin.site.register(Variation, VariationAdmin)
admin.site.register(reviewRating)