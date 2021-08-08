import bcrypt
import json

from django.http.response import JsonResponse
from django.db            import transaction
from django.db.models     import Case, When, Value
from django.views         import View

from .models              import (
    Post, Tag, PostTag
)
from users.models         import User
from users.decorators     import login_required
import my_settings

class BoardWriteView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.body)           
            board_category_id = data['board_category_id']
            post_category_id  = data['post_category_id']
            title             = data['title']
            content           = data['content'] 
            password          = data['password']
            tag_names         = data.get('tag_names')
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

class BoardRewriteView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.body)  
            post_id           = data['post_id']         
            title             = data['title']
            content           = data['content'] 
            password          = data['password']
            tag_names         = data.get('tag_names')
            # file            = request.FILES.get('filename') ## 파일 첨부는 추가 기능으로 구현

            post              = Post.objects.get(id=post_id)

            if not bcrypt.checkpw(password.encode('UTF-8'), post.password.encode('UTF-8')):
                return JsonResponse({'message' : 'INVALID_POST_PASSWORD'}, status=401)

            with transaction.atomic():
                post.title      = title
                post.content    = content
                
                post.save()

                before_update_posttag = post.posttag_set.all()
                before_update_posttag.delete() if before_update_posttag else None

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

            return JsonResponse({'message' : 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)
        except Post.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_POST_ID'}, status=401)

class BoardDeleteView(View):
    @login_required
    def post(self, request):
        try:
            data     = json.loads(request.body)
            post_id  = data['post_id']
            password = data['password']

            post     = Post.objects.get(id=post_id)

            if not bcrypt.checkpw(password.encode('UTF-8'), post.password.encode('UTF-8')):
                return JsonResponse({'message' : 'INVALID_POST_PASSWORD'}, status=401)
            
            post.delete()
        
            return JsonResponse({'message' : 'SUCCESS'}, status=200)
            
        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)
        except Post.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_POST_ID'}, status=401)

class BoardListView(View):
    def get(self, request):
        # 정렬: 내림차순, 공지 게시글 항상 위
        # 페이지 당 15개씩 - > 페이지 정보 쿼리스트링으로 받아야 함
        page_num  = int(request.GET.get('page', 1))
        limit     = 15
        start     = (page_num-1) * limit
        end       = page_num     * limit

        post_type_ordering = Case(When(
            post_category_id=3, then=1),
            default=2
        )
        
        post_list = Post.objects.all().annotate(ordering=post_type_ordering).order_by(
            'ordering',
            '-group_id'
        )[start:end] 

        result    = [{
            'id'            : post.id,
            'title'         : post.title,
            'post_category' : post.post_category.name,
            'writer'        : post.user.nickname,
            'final_updated' : post.updated_at,
            'views'         : post.views
        } for post in post_list]

        return JsonResponse({'reuslt' : result}, status=200)