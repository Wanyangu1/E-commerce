from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Coupon

def toggle_active_status(modeladmin, request, queryset):
    """Toggle the active status of selected coupons."""
    for coupon in queryset:
        coupon.active = not coupon.active
        coupon.save()
toggle_active_status.short_description = "Toggle Active Status"

def active_status(obj):
    """Returns a color-coded active status badge."""
    if obj.active:
        return mark_safe('<span style="color: green; font-weight: bold;">✔ Active</span>')
    return mark_safe('<span style="color: red; font-weight: bold;">✖ Inactive</span>')

active_status.short_description = "Status"

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Customizes the Coupon model in the admin panel."""
    list_display = ['code', 'valid_from_display', 'valid_to_display', 'discount', active_status]
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']
    ordering = ['-valid_from']
    actions = [toggle_active_status]

    def valid_from_display(self, obj):
        """Formats the 'valid_from' field for better readability."""
        return obj.valid_from.strftime('%b %d, %Y %H:%M')
    valid_from_display.short_description = "Valid From"

    def valid_to_display(self, obj):
        """Formats the 'valid_to' field for better readability."""
        return obj.valid_to.strftime('%b %d, %Y %H:%M')
    valid_to_display.short_description = "Valid To"
