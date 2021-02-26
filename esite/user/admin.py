from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from esite.user.models import SNEKCustomer

from .models import SNEKCustomer


class UserAdmin(ModelAdmin):
    model = SNEKCustomer
    menu_label = "Users"
    menu_icon = "user"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False

    # Listed in the user overview
    list_display = ("date_joined", "username", "email")
    search_fields = ("date_joined", "username", "email")


modeladmin_register(UserAdmin)
