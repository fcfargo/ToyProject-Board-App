from django               import views
import bcrypt
import json

from django.http.response import JsonResponse
from django.db            import transaction
from django.views         import View

from .models              import (
    Post, Tag, PostTag
)
from users.models         import User
from users.decorators     import login_required
import my_settings

class BoardwriteView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.body)           
            board_category_id = data['board_category_id']
            post_category_id  = data['post_category_id']
            title             = data['title']
            content           = data['content'] 
            password          = data['password']
            tag_names         = data['tag_names']
            ip_address        = self.get_client_ip(request)
            # file              = request.FILES.get('filename') ## 파일 첨부는 추가 기능으로 구현

            with transaction.atomic():
                post = Post(
                    board_category_id = board_category_id,
                    user_id           = request.user.id,
                    post_category_id  = post_category_id,
                    title             = title,
                    content           = content,
                    ip_address        = ip_address,
                    password          = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
                )
                post.save()

                if tag_names:        
                    for tag_name in tag_names.replace(" ","").split(','):

                        tag, is_created = Tag.objects.get_or_create(
                            name=tag_name
                        )
                        post_tag = PostTag(
                            post_id = post.id,
                            tag_id  = tag.id 
                        )
                        post_tag.save()

                post.group_id = post.id
                post.save()
  
            return JsonResponse({'message' : 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip