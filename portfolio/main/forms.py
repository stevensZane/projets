from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import *
import os

class ProjectForm(forms.ModelForm):
    """Formulaire pour créer/modifier un projet"""
    class Meta:
        model = Project
        fields = [
            'title', 'short_description', 'full_description', 
            'project_type', 'category', 'tech_stack', 'thumbnail',
            'video_url', 'documentation_pdf', 'github_url', 
            'live_demo_url', 'featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Titre du projet'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Description courte (max 300 caractères)',
                'rows': 3
            }),
            'full_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 markdown-editor',
                'placeholder': 'Description complète en Markdown',
                'rows': 10
            }),
            'project_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'tech_stack': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://youtube.com/...'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://github.com/...'
            }),
            'live_demo_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://demo.com/...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tech_stack'].widget.attrs.update({'size': '6'})

class ProjectImageForm(forms.ModelForm):
    """Formulaire pour les images du projet"""
    class Meta:
        model = ProjectImage
        fields = ['image', 'alt_text', 'order']
        widgets = {
            'alt_text': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'placeholder': 'Description de l\'image'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
                'min': '0'
            }),
        }

class ProjectTypeForm(forms.ModelForm):
    """Formulaire pour les types de projet"""
    class Meta:
        model = ProjectType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Ex: Application Web'
            }),
        }

class CategoryForm(forms.ModelForm):
    """Formulaire pour les catégories"""
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Ex: Développement Web'
            }),
        }


class TechStackForm(forms.ModelForm):
    """Formulaire avec sélection d'icône existante"""
    class Meta:
        model = TechStack
        fields = ['name', 'icon_filename']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Ex: Django, React, etc.'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Chercher les icônes dans le dossier
        icons_dir = os.path.join(settings.STATICFILES_DIRS[0], 'icons')
        icon_choices = [('', '--- Sélectionner une icône ---')]
        
        if os.path.exists(icons_dir):
            svg_files = [f for f in os.listdir(icons_dir) if f.lower().endswith('.svg')]
            svg_files.sort()
            
            for svg in svg_files:
                display_name = svg.replace('.svg', '').replace('.SVG', '').replace('-', ' ').replace('_', ' ').title()
                icon_choices.append((svg, f"{display_name}"))
        
        # Créer un champ select avec les icônes disponibles
        self.fields['icon_filename'] = forms.ChoiceField(
            choices=icon_choices,
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            label="Icône",
            required=True
        )

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'votre@email.com'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[150px]',
                'placeholder': 'Votre message...',
                'rows': 5
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        # Send email notification
        if settings.EMAIL_HOST_USER:
            try:
                send_mail(
                    subject=f'Nouveau message de {instance.name}',
                    message=f"Nom: {instance.name}\nEmail: {instance.email}\n\nMessage:\n{instance.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except:
                pass
        
        return instance