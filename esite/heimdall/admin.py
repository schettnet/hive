from wagtail.contrib.modeladmin.helpers.permission import PermissionHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import AsyncHeimdallGeneration, License


class LogEntryPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False

    # def user_can_inspect_obj(self, user, obj):
    #     return True

    def user_can_edit_obj(self, user, obj):
        return False


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


class LogAdmin(ModelAdmin):
    model = AsyncHeimdallGeneration
    menu_label = "Generation Log"
    menu_icon = "fa-history"

    permission_helper_class = LogEntryPermissionHelper

    # Listed in the user overview
    list_display = (
        "id",
        "license",
        "bridge_drop_binary_name",
        "bridge_drop_binary_saved",
        "updated_at",
        "created_at",
    )
    search_fields = ("created_at", "license")


class HeimdallAdmin(ModelAdminGroup):
    menu_label = "Heimdall"
    menu_icon = "fa-flask"
    menu_order = 200

    items = (
        LicenseAdmin,
        LogAdmin,
    )


modeladmin_register(HeimdallAdmin)

# SPDX-License-Identifier: (EUPL-1.2)
# Copyright © 2021 Nico Schett
