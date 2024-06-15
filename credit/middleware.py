def product_middleware(get_response):
    def middleware(request):
        # Attach an empty list to the request object
        request.product_ids = []
        response = get_response(request)
        return response

    return middleware