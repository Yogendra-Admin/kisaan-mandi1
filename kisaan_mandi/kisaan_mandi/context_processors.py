def selected_language(request):
    """Inject the user's selected language ('en', 'hi', 'ne') and notifications into every template context."""
    lang = request.COOKIES.get('km_lang', 'en')
    if lang not in ('en', 'hi', 'ne'):
        lang = 'en'
        
    context = {'selected_lang': lang}
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        from django.apps import apps
        try:
            Notification = apps.get_model('orders', 'Notification')
            notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:8]
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            context['notifications'] = notifs
            context['unread_notifications_count'] = unread_count
        except (LookupError, ValueError):
            pass
            
    return context
