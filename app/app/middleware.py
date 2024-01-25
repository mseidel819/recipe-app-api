class AddBearerTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add your logic to retrieve the bearer token, e.g., from the session or database
        session_token_cookie = request.COOKIES.get('next-auth.session-token')

        # Add the Authorization header if the token is available
        if request.path.startswith('/api/blog-recipes/favoridgdfte'):
            if session_token_cookie:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {session_token_cookie}"

        response = self.get_response(request)
        return response