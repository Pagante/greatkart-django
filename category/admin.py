from django.contrib import admin
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('category_name',)}

    list_display = ('id', 'category_name', 'slug')
    list_display_links = ('id', 'category_name')


admin.site.register(Category, CategoryAdmin)
