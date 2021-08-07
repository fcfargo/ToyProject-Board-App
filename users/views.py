import bcrypt
import json

from django.http.response import JsonResponse
from django.views         import View

from .models              import User
import my_settings

class SignupView(View):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            name     = data['name']
            password = data['password']
            email    = data['email']
            nickname = data['nickname']

            if not my_settings.NAME_CHECK.match(name):
                return JsonResponse({'message' : 'INVALID_NAME_VALUE'}, status = 400)

            if not my_settings.PASSWORD_CHECK.match(password):
                return JsonResponse({'message' : 'INVALID_PASSWORD_VALUE'}, status = 400)
            
            if not my_settings.EMAIL_CHECK.match(email):
                return JsonResponse({'message' : 'INVALID_EMAIL_VALUE'}, status = 400)

            if not my_settings.NICKNAME_CHECK.match(nickname):
                return JsonResponse({'message' : 'INVALID_NICKNAME_VALUE'}, status = 400)

            if User.objects.filter(name=name).exists():
                return JsonResponse({'message' : 'DUPLICATE_NAME_ERROR'}, status = 400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'message' : 'DUPLICATE_EMAIL_ERROR'}, status = 400)

            hashed_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')

            user = User(
                name     = name,
                password = hashed_password,
                email    = email,
                nickname = nickname
            )    
            user.save()

            return JsonResponse({'message' : 'SUCCESS'}, status = 200)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)