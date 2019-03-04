from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from .models import *


def get_change_view_link(instance, link_name, query=None):
    url = reverse(
        'admin:{}_{}_change'.format(
            instance._meta.app_label,
            instance._meta.object_name.lower()
        ),
        args=(instance.pk,)
    )

    if query:
        url = "{}?{}".format(url, query)

    return mark_safe('<a href="{}">{}</a>'.format(url, link_name))


@admin.register(Address)
class AddressModelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'details_link',
        'address_1',
        'address_2',
        'city',
        'region',
        'country',
        'region_code',
    )

    list_display_links = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = 'details'


@admin.register(Buyer)
class BuyerModelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'details_link',
        'full_name',
        'email',
        'phone_number',
        'shipping_address',
    )

    list_display_links = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = 'details'


@admin.register(CreditCard)
class CreditCardModelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'details_link',
        'description',
        'display',
    )

    list_display_links = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = 'details'


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'details_link',
        'description',
    )

    list_display_links = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = 'details'


@admin.register(Bot)
class BotModelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'details_link',
        'description',
    )

    list_display_links = (
        'details_link',
    )

    def details_link(self, obj):
        return get_change_view_link(obj, 'Details')
    details_link.short_description = 'details'
