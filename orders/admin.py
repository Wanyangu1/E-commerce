from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from .models import Order, OrderItem
import csv
import datetime

# ----- Utility Functions -----

def order_detail(obj):
    """Generates a clickable button to view order details in the admin panel."""
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}" class="btn btn-info btn-sm text-white"><i class="fas fa-eye"></i> View</a>')

order_detail.short_description = "Order Details"

def order_pdf(obj):
    """Generates a downloadable PDF invoice button."""
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}" class="btn btn-danger btn-sm text-white"><i class="fas fa-file-pdf"></i> Invoice</a>')

order_pdf.short_description = "Invoice"

def paid_status(obj):
    """Displays a payment status icon with a tooltip."""
    if obj.paid:
        return mark_safe('<span title="Paid"><i class="fas fa-check-circle text-success"></i></span>')
    return mark_safe('<span title="Not Paid"><i class="fas fa-times-circle text-danger"></i></span>')

paid_status.short_description = "Paid Status"

def export_to_csv(modeladmin, request, queryset):
    """
    Exports selected orders to a CSV file.
    Handles encoding and date formatting properly.
    """
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name_plural}.csv'
    
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    
    # Header row
    writer.writerow([field.verbose_name.capitalize() for field in fields])
    
    # Data rows
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name, '')
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')  # Standard datetime format
            row.append(value if value is not None else '')  # Ensures no 'None' values
        writer.writerow(row)
    
    return response

export_to_csv.short_description = "Export Selected Orders to CSV"

# ----- Admin Customization -----

class OrderItemInline(admin.TabularInline):
    """Displays order items inline in the admin panel."""
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Customizes the Order model display in the Django Admin panel."""
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'city',
        paid_status, 'created', 'updated', order_detail, order_pdf
    ]
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email']
    ordering = ['-created']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
