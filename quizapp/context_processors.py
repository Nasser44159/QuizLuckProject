def custom_user_context(request):
    if request.user.is_authenticated:
        return {
            'user_full_name': f"{request.user.first_name} {request.user.last_name}"
        }
    return {}
