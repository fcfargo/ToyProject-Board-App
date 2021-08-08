import jwt

from django.http.response import JsonResponse

from .models              import User
import my_settings

def login_required(func):
    def decorator(self, request, *args, **kwargs):
        try:
            access_token  = request.headers['Authorization']
            decoded_token = jwt.decode(access_token, my_settings.SECRET['secret'], algorithms='HS256')

            user = User.objects.get(id=decoded_token['user_id'])
            
            request.user = user
            return func(self, request)

        except User.DoesNotExist:
            return JsonResponse({'message':'UNKNOWN_USER'}, status=400)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

        except jwt.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status=400)
            
    return decorator