from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from accounting.models import (CurrencyCBR, Product, Transaction,
                               TransactionCategoryTree, TransactionRow, Wallet)


class TransactionRowInline(admin.TabularInline):
    model = TransactionRow
    extra = 3


admin.site.register(
    TransactionCategoryTree,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
        'title',
    ),
    list_display_links=(
        'indented_title',
    ),
    search_fields=(
        'title',
    ),
    autocomplete_fields=('parent', 'user')
)

admin.site.register(Transaction, inlines=[TransactionRowInline], list_display=(
    't_type', 'wallet', 'user', 'category', 'amount', 'tax', 'description', 'date'), autocomplete_fields=('wallet', 'user', 'category'))
admin.site.register(TransactionRow, list_display=(
    'product', 'transaction', 'amount', 'quantity', 'tax'))
admin.site.register(Wallet, list_display=('user', 'title', 'currency', 'balance'),
                    autocomplete_fields=('user', 'currency'), search_fields=('user', 'currency', 'title'))
admin.site.register(CurrencyCBR, list_display=(
    'num_code', 'char_code', 'name'), search_fields=('num_code', 'char_code', 'name'))
admin.site.register(Product, list_display=('user', 'title', 'description'))
