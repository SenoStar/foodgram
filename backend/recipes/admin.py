from django.contrib import admin

from .models import (
    Tag,
    User
)

admin.site.register(Tag)
admin.site.register(User)
