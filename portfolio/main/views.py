# main/views.py - COMPLÈTEMENT MIS À JOUR
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import *
from .forms import *

# ==================== VUES PUBLIQUES ====================

def home(request):
    featured_projects = Project.objects.filter(featured=True).select_related('project_type', 'category').prefetch_related('tech_stack', 'images')[:6]
    recent_projects = Project.objects.all().select_related('project_type', 'category').prefetch_related('tech_stack')[:3]
    tech_stack = TechStack.objects.all()[:12]
    
    context = {
        'featured_projects': featured_projects,
        'recent_projects': recent_projects,
        'tech_stack': tech_stack,
        'page_title': 'Accueil',
    }
    return render(request, 'main/home.html', context)

def project_list(request):
    projects = Project.objects.all().select_related('project_type', 'category').prefetch_related('tech_stack', 'images')
    
    # Filtres
    project_type = request.GET.get('type')
    category = request.GET.get('category')
    tech = request.GET.get('tech')
    search = request.GET.get('search')
    
    if project_type:
        projects = projects.filter(project_type__slug=project_type)
    if category:
        projects = projects.filter(category__slug=category)
    if tech:
        projects = projects.filter(tech_stack__slug=tech)
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search) |
            Q(full_description__icontains=search) |
            Q(tech_stack__name__icontains=search)
        ).distinct()
    
    # Options de filtre
    project_types = ProjectType.objects.all()
    categories = Category.objects.all()
    tech_stack = TechStack.objects.all()
    
    context = {
        'projects': projects,
        'project_types': project_types,
        'categories': categories,
        'tech_stack': tech_stack,
        'selected_type': project_type,
        'selected_category': category,
        'selected_tech': tech,
        'search_query': search or '',
        'page_title': 'Projets',
    }
    return render(request, 'main/project_list.html', context)

def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.select_related('project_type', 'category').prefetch_related('tech_stack', 'images'),
        slug=slug
    )
    
    # Track view
    metric, created = ProjectMetric.objects.get_or_create(project=project)
    metric.increment_view()
    
    # Projets similaires
    related_projects = Project.objects.filter(
        Q(project_type=project.project_type) | Q(category=project.category)
    ).exclude(id=project.id).distinct()[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'page_title': project.title,
    }
    return render(request, 'main/project_detail.html', context)

def about(request):
    context = {'page_title': 'À propos'}
    return render(request, 'main/about.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'main/contact_success.html', {'page_title': 'Message envoyé'})
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'page_title': 'Contact',
    }
    return render(request, 'main/contact.html', context)

@require_POST
def track_click(request):
    try:
        data = json.loads(request.body)
        project_slug = data.get('project_slug')
        click_type = data.get('type')
        
        if not project_slug or not click_type:
            return JsonResponse({'error': 'Données manquantes'}, status=400)
        
        project = get_object_or_404(Project, slug=project_slug)
        metric, created = ProjectMetric.objects.get_or_create(project=project)
        
        if click_type == 'github':
            metric.increment_github_click()
        elif click_type == 'demo':
            metric.increment_demo_click()
        elif click_type == 'doc':
            metric.increment_doc_click()
        else:
            return JsonResponse({'error': 'Type de clic invalide'}, status=400)
        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_filter_data(request):
    project_types = list(ProjectType.objects.values('slug', 'name'))
    categories = list(Category.objects.values('slug', 'name'))
    tech_stack = list(TechStack.objects.values('slug', 'name'))
    
    return JsonResponse({
        'project_types': project_types,
        'categories': categories,
        'tech_stack': tech_stack,
    })

# ==================== VUES ADMIN ====================

@login_required
def admin_dashboard(request):
    """Tableau de bord admin"""
    total_projects = Project.objects.count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(read=False).count()
    featured_projects = Project.objects.filter(featured=True).count()
    
    # Métriques récentes
    week_ago = timezone.now() - timedelta(days=7)
    recent_metrics = ProjectMetric.objects.filter(last_updated__gte=week_ago).aggregate(
        total_views=Sum('view_count'),
        total_github_clicks=Sum('github_click_count'),
        total_demo_clicks=Sum('demo_click_count')
    )
    
    # Projets récents
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
    # Messages récents
    recent_messages = ContactMessage.objects.all().order_by('-created_at')[:5]
    
    # Distribution par type
    projects_by_type = Project.objects.values('project_type__name').annotate(
        count=Count('id')
    )
    
    context = {
        'page_title': 'Tableau de bord',
        'total_projects': total_projects,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'featured_projects': featured_projects,
        'recent_metrics': recent_metrics,
        'recent_projects': recent_projects,
        'recent_messages': recent_messages,
        'projects_by_type': projects_by_type,
    }
    return render(request, 'main/admin/dashboard.html', context)

# ==================== GESTION DES PROJETS ====================

@login_required
def admin_projects(request):
    """Liste des projets"""
    projects = Project.objects.all().select_related('project_type', 'category')
    
    # Filtres
    project_type = request.GET.get('type')
    category = request.GET.get('category')
    featured = request.GET.get('featured')
    search = request.GET.get('search')
    
    if project_type:
        projects = projects.filter(project_type__slug=project_type)
    if category:
        projects = projects.filter(category__slug=category)
    if featured:
        projects = projects.filter(featured=(featured == 'true'))
    if search:
        projects = projects.filter(title__icontains=search)
    
    project_types = ProjectType.objects.all()
    categories = Category.objects.all()
    
    context = {
        'page_title': 'Gestion des projets',
        'projects': projects,
        'project_types': project_types,
        'categories': categories,
        'selected_type': project_type,
        'selected_category': category,
        'selected_featured': featured,
        'search_query': search or '',
    }
    return render(request, 'main/admin/projects.html', context)

@login_required
def admin_project_create(request):
    """Créer un nouveau projet"""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Projet "{project.title}" créé avec succès!')
            return redirect('admin_project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'page_title': 'Créer un projet',
        'form': form,
        'project_types': ProjectType.objects.all(),
        'categories': Category.objects.all(),
        'tech_stack': TechStack.objects.all(),
    }
    return render(request, 'main/admin/project_form.html', context)

@login_required
def admin_project_edit(request, project_id):
    """Modifier un projet existant"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Projet "{project.title}" mis à jour!')
            return redirect('admin_project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'page_title': f'Modifier {project.title}',
        'form': form,
        'project': project,
        'project_types': ProjectType.objects.all(),
        'categories': Category.objects.all(),
        'tech_stack': TechStack.objects.all(),
    }
    return render(request, 'main/admin/project_form.html', context)

@login_required
def admin_project_detail(request, project_id):
    """Détail d'un projet"""
    project = get_object_or_404(Project.objects.prefetch_related('tech_stack', 'images'), id=project_id)
    
    # Formulaire pour ajouter des images
    image_form = ProjectImageForm()
    
    if request.method == 'POST':
        # Actions
        if 'toggle_featured' in request.POST:
            project.featured = not project.featured
            project.save()
            messages.success(request, f'Projet {"mis en vedette" if project.featured else "retiré des vedettes"}!')
            return redirect('admin_project_detail', project_id=project.id)
        
        elif 'add_image' in request.POST:
            image_form = ProjectImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                project_image = image_form.save(commit=False)
                project_image.project = project
                project_image.save()
                messages.success(request, 'Image ajoutée!')
                return redirect('admin_project_detail', project_id=project.id)
        
        elif 'delete_project' in request.POST:
            project_title = project.title
            project.delete()
            messages.success(request, f'Projet "{project_title}" supprimé!')
            return redirect('admin_projects')
    
    # Métriques
    metrics = project.metrics.first()
    
    context = {
        'page_title': f'{project.title}',
        'project': project,
        'metrics': metrics,
        'image_form': image_form,
    }
    return render(request, 'main/admin/project_detail.html', context)

@login_required
def admin_project_delete_image(request, image_id):
    """Supprimer une image de projet"""
    image = get_object_or_404(ProjectImage, id=image_id)
    project_id = image.project.id
    image.delete()
    messages.success(request, 'Image supprimée!')
    return redirect('admin_project_detail', project_id=project_id)

# ==================== GESTION DES MESSAGES ====================

@login_required
def admin_messages(request):
    """Liste des messages"""
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Filtres
    read_status = request.GET.get('read')
    search = request.GET.get('search')
    
    if read_status == 'unread':
        messages_list = messages_list.filter(read=False)
    elif read_status == 'read':
        messages_list = messages_list.filter(read=True)
    
    if search:
        messages_list = messages_list.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(message__icontains=search)
        )
    
    context = {
        'page_title': 'Messages de contact',
        'messages': messages_list,
        'total_messages': messages_list.count(),
        'unread_count': ContactMessage.objects.filter(read=False).count(),
    }
    return render(request, 'main/admin/messages.html', context)

@login_required
def admin_message_detail(request, message_id):
    """Détail d'un message"""
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Marquer comme lu
    if not message.read:
        message.read = True
        message.save(update_fields=['read'])
    
    if request.method == 'POST':
        if 'delete_message' in request.POST:
            message.delete()
            messages.success(request, "Message supprimé!")
            return redirect('admin_messages')
    
    context = {
        'page_title': f'Message de {message.name}',
        'message': message,
    }
    return render(request, 'main/admin/message_detail.html', context)

# ==================== GESTION DES CATÉGORIES/TYPES/TECH ====================

@login_required
def admin_categories(request):
    """Gérer les catégories"""
    if request.method == 'POST':
        if 'add_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Catégorie ajoutée!')
                return redirect('admin_categories')
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            messages.success(request, 'Catégorie supprimée!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    
    categories = Category.objects.all()
    
    context = {
        'page_title': 'Catégories',
        'categories': categories,
        'form': form,
    }
    return render(request, 'main/admin/categories.html', context)

@login_required
def admin_project_types(request):
    """Gérer les types de projet"""
    if request.method == 'POST':
        if 'add_type' in request.POST:
            form = ProjectTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Type de projet ajouté!')
                return redirect('admin_project_types')
        elif 'delete_type' in request.POST:
            type_id = request.POST.get('type_id')
            project_type = get_object_or_404(ProjectType, id=type_id)
            project_type.delete()
            messages.success(request, 'Type de projet supprimé!')
            return redirect('admin_project_types')
    else:
        form = ProjectTypeForm()
    
    project_types = ProjectType.objects.all()
    
    context = {
        'page_title': 'Types de projet',
        'project_types': project_types,
        'form': form,
    }
    return render(request, 'main/admin/project_types.html', context)

@login_required
def admin_tech_stack(request):
    """Gérer les technologies"""
    if request.method == 'POST':
        if 'add_tech' in request.POST:
            form = TechStackForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Technologie ajoutée!')
                return redirect('admin_tech_stack')
        elif 'delete_tech' in request.POST:
            tech_id = request.POST.get('tech_id')
            tech = get_object_or_404(TechStack, id=tech_id)
            tech.delete()
            messages.success(request, 'Technologie supprimée!')
            return redirect('admin_tech_stack')
    else:
        form = TechStackForm()
    
    tech_stack = TechStack.objects.all()
    
    context = {
        'page_title': 'Technologies',
        'tech_stack': tech_stack,
        'form': form,
    }
    return render(request, 'main/admin/tech_stack.html', context)

# ==================== ANALYTICS ET PARAMÈTRES ====================

@login_required
def admin_analytics(request):
    """Analyses et statistiques"""
    projects = Project.objects.all()
    
    # Top projets
    top_projects = []
    for project in projects:
        metric = project.metrics.first()
        if metric:
            top_projects.append({
                'project': project,
                'views': metric.view_count,
                'github_clicks': metric.github_click_count,
                'demo_clicks': metric.demo_click_count,
                'doc_clicks': metric.doc_click_count
            })
    
    top_projects = sorted(top_projects, key=lambda x: x['views'], reverse=True)[:10]
    
    # Stats mensuelles
    month_ago = timezone.now() - timedelta(days=30)
    monthly_stats = ProjectMetric.objects.filter(last_updated__gte=month_ago).aggregate(
        total_views=Sum('view_count'),
        total_github_clicks=Sum('github_click_count'),
        total_demo_clicks=Sum('demo_click_count')
    )
    
    context = {
        'page_title': 'Analytiques',
        'top_projects': top_projects,
        'monthly_stats': monthly_stats,
        'total_projects': projects.count(),
    }
    return render(request, 'main/admin/analytics.html', context)

@login_required
def admin_settings(request):
    """Paramètres"""
    if request.method == 'POST':
        if 'clear_metrics' in request.POST:
            ProjectMetric.objects.all().delete()
            messages.success(request, "Métriques réinitialisées!")
        
        elif 'generate_report' in request.POST:
            messages.info(request, "Rapport généré!")
        
        return redirect('admin_settings')
    
    context = {
        'page_title': 'Paramètres',
    }
    return render(request, 'main/admin/settings.html', context)