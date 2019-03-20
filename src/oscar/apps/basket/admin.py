from django.contrib import admin

from oscar.core.loading import get_model, is_model_registered

Line = get_model('basket', 'line')


class LineInline(admin.TabularInline):
    model = Line
    readonly_fields = ('line_reference', 'product', 'price_excl_tax',
                       'price_incl_tax', 'price_currency', 'stockrecord')


class LineAdmin(admin.ModelAdmin):
    list_display = ('id', 'basket', 'product', 'stockrecord', 'quantity',
                    'price_excl_tax', 'price_currency', 'date_created')
    readonly_fields = ('basket', 'stockrecord', 'line_reference', 'product',
                       'price_currency', 'price_incl_tax', 'price_excl_tax',
                       'quantity')


class BasketAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'status', 'num_lines',
                    'contains_a_voucher', 'date_created', 'date_submitted',
                    'time_before_submit')
    readonly_fields = ('owner', 'date_merged', 'date_submitted')
    inlines = [LineInline]


if not is_model_registered('basket','basket'):
    admin.site.register(get_model('basket', 'BasketAdmin'))

if not is_model_registered('basket', 'Line'):
    admin.site.register(get_model('basket', 'Line'), 'LineAdmin')

if not is_model_registered('basket', 'LineAttribute'):
    admin.site.register(get_model('basket', 'LineAttribuute'))
