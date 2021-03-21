from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import License


class LicenseAdmin(ModelAdmin):
    model = License
    menu_label = "Licences"
    menu_icon = "fa-id-card"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False

    # Listed in the user overview
    list_display = ("key", "owner", "remaining_uses", "is_active")
    search_fields = ("owner", "is_active")


modeladmin_register(LicenseAdmin)

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2021 Nico Schett
