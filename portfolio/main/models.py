# models.py - UPDATED (removed markdownfield dependency)
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import URLValidator
import markdown
import os
from django.conf import settings
from django.utils.html import mark_safe

class ProjectType(models.Model):
    name = models.CharField(max_length=100, verbose_name="nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name = "type de projet"
        verbose_name_plural = "types de projet"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class TechStack(models.Model):
    name = models.CharField(max_length=100, verbose_name="nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon_filename = models.CharField(
        max_length=100, 
        verbose_name="fichier icône",
        help_text="Nom du fichier dans le dossier icons/ (ex: python.svg)",
        default="default.svg"  # ← AJOUTEZ UN DEFAULT
    )
    
    class Meta:
        verbose_name = "technologie"
        verbose_name_plural = "technologies"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def icon_url(self):
        """URL complète de l'icône"""
        return f"/static/icons/{self.icon_filename}"
    
    @property
    def icon_path(self):
        """Chemin physique du fichier"""
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
        return os.path.join(static_dir, 'icons', self.icon_filename)
    
    @property
    def icon_exists(self):
        """Vérifie si le fichier existe"""
        return os.path.exists(self.icon_path)

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.TextField(max_length=300, verbose_name="description courte")
    full_description = models.TextField(verbose_name="description complète (Markdown)")
    project_type = models.ForeignKey(ProjectType, on_delete=models.SET_NULL, null=True, verbose_name="type de projet")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="catégorie")
    tech_stack = models.ManyToManyField(TechStack, verbose_name="technologies")
    thumbnail = models.ImageField(upload_to='project_thumbnails/', verbose_name="miniature")
    video_url = models.URLField(max_length=500, blank=True, verbose_name="URL vidéo")
    documentation_pdf = models.FileField(upload_to='project_docs/', blank=True, null=True, verbose_name="PDF documentation")
    github_url = models.URLField(max_length=500, verbose_name="URL GitHub")
    live_demo_url = models.URLField(max_length=500, blank=True, verbose_name="URL démo")
    featured = models.BooleanField(default=False, verbose_name="en vedette")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="date de création")
    
    class Meta:
        verbose_name = "projet"
        verbose_name_plural = "projets"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def full_description_html(self):
        """Convert markdown to HTML"""
        return mark_safe(markdown.markdown(self.full_description))

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name="projet")
    image = models.ImageField(upload_to='project_images/', verbose_name="image")
    alt_text = models.CharField(max_length=200, verbose_name="texte alternatif")
    order = models.PositiveIntegerField(default=0, verbose_name="ordre")
    
    class Meta:
        verbose_name = "image de projet"
        verbose_name_plural = "images de projet"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.project.title} - {self.alt_text}"

class ProjectMetric(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='metrics', verbose_name="projet")
    view_count = models.PositiveIntegerField(default=0, verbose_name="vues")
    github_click_count = models.PositiveIntegerField(default=0, verbose_name="clics GitHub")
    demo_click_count = models.PositiveIntegerField(default=0, verbose_name="clics démo")
    doc_click_count = models.PositiveIntegerField(default=0, verbose_name="clics documentation")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="dernière mise à jour")
    
    class Meta:
        verbose_name = "métrique de projet"
        verbose_name_plural = "métriques de projet"
    
    def __str__(self):
        return f"Métriques pour {self.project.title}"
    
    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count', 'last_updated'])
    
    def increment_github_click(self):
        self.github_click_count += 1
        self.save(update_fields=['github_click_count', 'last_updated'])
    
    def increment_demo_click(self):
        self.demo_click_count += 1
        self.save(update_fields=['demo_click_count', 'last_updated'])
    
    def increment_doc_click(self):
        self.doc_click_count += 1
        self.save(update_fields=['doc_click_count', 'last_updated'])

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="nom")
    email = models.EmailField(verbose_name="email")
    message = models.TextField(verbose_name="message")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="date d'envoi")
    read = models.BooleanField(default=False, verbose_name="lu")
    
    class Meta:
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message de {self.name} - {self.created_at.strftime('%Y-%m-%d')}"