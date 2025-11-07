from django.contrib import admin

from .models import DesignRequest, CustomUser

admin.site.register(DesignRequest)
admin.site.register(CustomUser)