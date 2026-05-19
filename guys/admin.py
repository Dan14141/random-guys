from django.contrib import admin

from .models import Guy


@admin.register(Guy)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'gender', 'phone', 'email')
    search_fields = ('last_name', 'first_name', 'email', 'phone')
    list_filter = ('gender',)
