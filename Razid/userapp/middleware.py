# userapp/middleware.py

from django.shortcuts import redirect
from django.urls import resolve
from userapp.utils.encryption import encrypt_data, decrypt_data

class EncryptURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_info = request.path_info
        url_name = resolve(path_info).url_name
        
        if url_name not in ['home_redirect', 'home_with_id']:  # Skip already encrypted or home redirect view
            encrypted_url_name = encrypt_data(url_name)
            encrypted_path = path_info.replace(url_name, encrypted_url_name)
            return redirect(encrypted_path)

        response = self.get_response(request)
        return response
