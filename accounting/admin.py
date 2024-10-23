from django.contrib import admin
from accounting.models import Transaction, TransactionCategoryTree, TransactionRow, Wallet
from mptt.admin import DraggableMPTTAdmin

class TransactionRowInline(admin.TabularInline):
    model = TransactionRow
    extra = 3

class TransactionAdmin(admin.ModelAdmin):
    inlines = [
        TransactionRowInline
    ]

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
)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionRow)
admin.site.register(Wallet)