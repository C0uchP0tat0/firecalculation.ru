from django.contrib import admin
from .models import FireObject, FireLoad, Quantity


class FireObjectAdmin(admin.ModelAdmin):
    pass


class FireLoadtAdmin(admin.ModelAdmin):
    pass


class QuantityAdmin(admin.ModelAdmin):
    list_display = ['fire_object', 'fire_load', 'weight', 'material_Q']


admin.site.register(FireObject, FireObjectAdmin)
admin.site.register(FireLoad, FireLoadtAdmin)
admin.site.register(Quantity, QuantityAdmin)
