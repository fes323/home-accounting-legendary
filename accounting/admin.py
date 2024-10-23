from django.contrib import admin
from accounting.models import Transaction, TransactionCategoryTree, TransactionRow, Wallet


admin.site.register(Transaction)
admin.site.register(TransactionCategoryTree)
admin.site.register(TransactionRow)
admin.site.register(Wallet)