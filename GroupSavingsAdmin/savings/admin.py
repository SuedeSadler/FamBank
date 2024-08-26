from django.contrib import admin
from .models import Group, Contribution

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'created_at')
    search_fields = ('name', 'manager__username')

# Register the Contribution model
@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('group', 'member', 'amount', 'date')
    search_fields = ('group__name', 'member__username')