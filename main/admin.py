from django.contrib import admin
from .models import WaterData, ContactQuery, SurveyResult

@admin.register(WaterData)
class WaterDataAdmin(admin.ModelAdmin):
    list_display    = ('id', 'ph', 'turbidity', 'temperature', 'quality', 'disease', 'created_at')
    list_filter     = ('quality', 'created_at')
    search_fields   = ('quality', 'disease')
    ordering        = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display    = ('id', 'name', 'email', 'subject', 'is_read', 'created_at')
    list_filter     = ('is_read', 'created_at')
    search_fields   = ('name', 'email', 'subject', 'message')
    ordering        = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_editable   = ('is_read',)

@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display    = ('id', 'user', 'score', 'risk_level', 'created_at')
    list_filter     = ('risk_level', 'created_at')
    search_fields   = ('user', 'risk_level')
    ordering        = ('-created_at',)
    readonly_fields = ('user', 'score', 'risk_level', 'answers', 'created_at')