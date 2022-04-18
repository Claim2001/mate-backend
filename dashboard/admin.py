from django.contrib import admin
from .models import *


@admin.register(KnowledgeBaseModel)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'preview', 'category']


@admin.register(KnowledgeBookModel)
class KnowledgeBookAdmin(admin.ModelAdmin):
    list_display = ['kn_base', 'book', 'description']


@admin.register(KnowledgeVideoModel)
class KnowledgeVideoAdmin(admin.ModelAdmin):
    list_display = ['kn_base', 'video', 'description']


@admin.register(NotificationModel)
class NotificationModelAdmin(admin.ModelAdmin):
    list_display = ['to_user', 'seen']


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'status_payment', 'click_trans_id']


@admin.register(PaymeModel)
class PaymeModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'status_payment', 'paycom_transaction_id']


@admin.register(LogsModel)
class LogsModelAdmin(admin.ModelAdmin):
    list_display = ['url_type', 'merchant_trans_id']
