from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from .models import Category, Product

# ----- Utility Functions -----

def product_image_preview(obj):
    """Displays a small product image preview in Django admin."""
    if obj.image:
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
    return "No Image"

product_image_preview.short_description = "Image"

def stock_status(obj):
    """Displays a visual indicator for product availability."""
    if obj.available:
        return mark_safe('<span style="color: green; font-weight: bold;">✔ In Stock</span>')
    return mark_safe('<span style="color: red; font-weight: bold;">✖ Out of Stock</span>')

stock_status.short_description = "Stock"

def export_products_to_csv(modeladmin, request, queryset):
    """Exports selected products to a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    fields = ["Name", "Slug", "Price", "Availability", "Created", "Updated", "Image URL"]
    
    # Write header
    writer.writerow(fields)
    
    # Write data rows
    for obj in queryset:
        writer.writerow([
            obj.name, obj.slug, obj.price,
            "Available" if obj.available else "Out of Stock",
            obj.created.strftime("%Y-%m-%d"), obj.updated.strftime("%Y-%m-%d"),
            obj.image.url if obj.image else "No Image"
        ])
    
    return response

export_products_to_csv.short_description = "Export Selected Products to CSV"

# ----- Admin Customization -----

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin customization for product categories."""
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin customization for products."""
    list_display = ["name", product_image_preview, "slug", "price", "available", stock_status, "created", "updated"]
    list_filter = ["available", "created", "updated", "category"]
    search_fields = ["name", "category__name"]
    list_editable = ["price", "available"]
    prepopulated_fields = {"slug": ("name",)}
    actions = [export_products_to_csv]
    ordering = ["-created"]

    # Set non-editable fields as read-only
    readonly_fields = ["created", "updated"]

    fieldsets = (
        ("Product Information", {
            "fields": ("name", "slug", "category", "description", "price", "available")
        }),
        ("Image", {
            "fields": ("image",),
            "description": "Upload product image."
        }),
        ("Timestamps", {
            "fields": ("created", "updated"),
            "classes": ["collapse"]
        }),
    )
