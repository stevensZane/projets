# admin.py - UPDATED (removed markdownfield dependency)
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from .models import *

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Aperçu"

class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    can_delete = False
    readonly_fields = ('view_count', 'github_click_count', 'demo_click_count', 'doc_click_count', 'last_updated')
    max_num = 1
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return False

class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 20, 'class': 'markdown-editor'}),
        }
        help_texts = {
            'full_description': 'Utilisez la syntaxe Markdown pour formater votre texte.',
        }

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'project_type', 'category', 'featured', 'created_at', 'view_count', 'github_clicks')
    list_filter = ('project_type', 'category', 'featured', 'created_at')
    search_fields = ('title', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tech_stack',)
    inlines = [ProjectImageInline, ProjectMetricInline]
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'short_description', 'full_description', 'project_type', 'category', 'tech_stack')
        }),
        ('Médias', {
            'fields': ('thumbnail', 'video_url', 'documentation_pdf')
        }),
        ('Liens', {
            'fields': ('github_url', 'live_demo_url')
        }),
        ('Options', {
            'fields': ('featured', 'created_at')
        }),
    )
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
            'https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js',
            'admin/js/markdown-editor.js',
        )
    
    def view_count(self, obj):
        metric = obj.metrics.first()
        return metric.view_count if metric else 0
    view_count.short_description = "Vues"
    
    def github_clicks(self, obj):
        metric = obj.metrics.first()
        return metric.github_click_count if metric else 0
    github_clicks.short_description = "Clics GitHub"

@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_preview')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="object-fit: contain;" />', obj.icon.url)
        return "-"
    icon_preview.short_description = "Icône"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'read', 'message_preview')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = "Message"
    
    def has_add_permission(self, request):
        return False