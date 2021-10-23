import boto3
import bcrypt
import json
from datetime             import datetime

from django.http.response import JsonResponse
from django.db            import transaction
from django.db.models     import Case, When, Value
from django.views         import View
from django.db.models     import F

from .models              import Post, FileUpload

from users.models         import User
from users.decorators     import login_required
from .modules             import get_client_ip, create_s3_client
import my_settings

class BoardWriteView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.POST.get('json'))           
            board_category_id = data['board_category_id']
            post_category_id  = data['post_category_id']
            title             = data['title']
            content           = data['content'] 
            password          = data['password']
            tag_names         = data.get('tag_names')
            ip_address        = get_client_ip(self, request)
            files             = request.FILES.getlist('filename')

            if files:
                s3_client     = create_s3_client()
                bucket_name   = my_settings.BUCKET_NAME                   # AWS s3 버킷 이름
                aws_region    = my_settings.AWS_REGION                    # AWS s3 리전 
                file_urls     = []

                for file in files:
                    s3_client.upload_fileobj(                                
                        file,
                        bucket_name,
                        'board_file/' + file.name,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )
                    file_endpoint = file.name.replace(" ", "")
                    file_url = f'https://{bucket_name}.s3.{aws_region}.amazonaws.com/board_file/{file_endpoint}'
                    file_urls.append(file_url)

            with transaction.atomic():
                post = Post(
                    board_category_id = board_category_id,
                    user_id           = request.user.id,
                    post_category_id  = post_category_id,
                    title             = title,
                    content           = content,
                    ip_address        = ip_address,
                    password          = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8'),
                    tag               = tag_names 
                )
                post.save()

                post.group_id = post.id
                post.save()

                if files:
                    for file_url in file_urls:
                        fileupload = FileUpload(
                            post_id           = post.id,
                            path              = file_url
                        )
                        fileupload.save()

            return JsonResponse({'message' : 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)

class BoardRewriteView(View):
    @login_required
    def post(self, request):
        try:
            data                = json.loads(request.POST.get('json'))  
            post_id             = data['post_id']         
            title               = data['title']
            content             = data['content'] 
            password            = data['password']
            tag_names           = data.get('tag_names')
            files               = request.FILES.getlist('filename')

            post                = Post.objects.get(id=post_id)

            fileupload_list     = post.fileupload_set.all()

            if not bcrypt.checkpw(password.encode('UTF-8'), post.password.encode('UTF-8')):
                return JsonResponse({'message' : 'INVALID_POST_PASSWORD'}, status=401)

            if fileupload_list:
                s3_client       = create_s3_client()
                bucket_name     = my_settings.BUCKET_NAME                   # AWS s3 버킷 이름
                aws_region      = my_settings.AWS_REGION                    # AWS s3 리전 

                for obj in fileupload_list:
                    s3_client.delete_object(
                        Bucket  = bucket_name,
                        Key     = str(obj.path).split('amazonaws.com/')[-1]
                    )

            if files:
                s3_client         = create_s3_client()
                bucket_name       = my_settings.BUCKET_NAME
                aws_region        = my_settings.AWS_REGION
                file_urls         = []

                for file in files:
                    s3_client.upload_fileobj(                                
                        file,
                        bucket_name,
                        'board_file/' + file.name,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )

                    file_endpoint = file.name.replace(" ", "")
                    file_url = f'https://{bucket_name}.s3.{aws_region}.amazonaws.com/board_file/{file_endpoint}'
                    file_urls.append(file_url)

            with transaction.atomic():
                fileupload_list.delete()

                post.title      = title
                post.content    = content
                post.tag        = tag_names
                                
                post.save()

                if files:
                    for file_url in file_urls:
                        fileupload = FileUpload(
                            post_id           = post.id,
                            path              = file_url
                        )
                        fileupload.save()

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

            fileupload_list     = post.fileupload_set.all()

            if not bcrypt.checkpw(password.encode('UTF-8'), post.password.encode('UTF-8')):
                return JsonResponse({'message' : 'INVALID_POST_PASSWORD'}, status=401)

            if fileupload_list:
                s3_client       = create_s3_client()
                bucket_name     = my_settings.BUCKET_NAME                   # AWS s3 버킷 이름
                aws_region      = my_settings.AWS_REGION                    # AWS s3 리전 

                for obj in fileupload_list:
                    s3_client.delete_object(
                        Bucket  = bucket_name,
                        Key     = str(obj.path).split('amazonaws.com/')[-1]
                    )
            
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
        # 페이지 당 15개씩 가져오기
        try:
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
                '-group_id',
                'group_order'
            )[start:end] 

            result    = [{
                'id'            : post.id,
                'title'         : post.title,
                'post_category' : post.post_category.name,
                'writer'        : post.user.nickname,
                'final_updated' : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'views'         : post.views,
                'group_id'      : post.group_id,
                'group_order'   : post.group_order,
                'group_depth'   : post.group_depth
            } for post in post_list]

            return JsonResponse({'result' : result}, status=200)
        except ValueError:
            return JsonResponse({'message' : "ENTER page_number"}, status=400)

class BoardDetailView(View):
    def get(self, request, post_id=None):
        try:
            if not post_id:
                return JsonResponse({'message' : "ENTER post_id"}, status=400)

            post       = Post.objects.select_related('post_category', 'user').prefetch_related('fileupload_set').get(id=post_id)
            
            # views 업데이트 쿼리
            post.views = F('views')+1
            post.save()

            post_info =[{
                "post_category" : post.post_category.name,
                "writer"        : post.user.nickname,
                "title"         : post.title,
                "content"       : post.content,
                "ip_address"    : post.ip_address,
                "tag"           : post.tag.replace(" ", "").split(',') if post.tag else None,
                "updated_at"    : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                "file_uploads"  : [str(obj.path).split('/board_file/')[-1] for obj in post.fileupload_set.all()] if post.fileupload_set.all() else None
            }]

            return JsonResponse({'result' : post_info}, status=200)

        except Post.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_POST_ID'}, status=401)

class BoardReplyView(View):
    @login_required
    def post(self, request):
        try:
            data              = json.loads(request.POST.get('json'))
            post_id           = data['post_id']         
            title             = data['title']
            content           = data['content'] 
            password          = data['password']
            tag_names         = data.get('tag_names')
            ip_address        = get_client_ip(self,request)
            post_category_id  = 2
            files             = request.FILES.getlist('filename')

            mother_post       = Post.objects.get(id=post_id)

            child_post_list   = Post.objects.filter(
                group_id=mother_post.group_id, group_order__gt=mother_post.group_order 
            )

            if files:
                s3_client     = create_s3_client()
                bucket_name   = my_settings.BUCKET_NAME                   # AWS s3 버킷 이름
                aws_region    = my_settings.AWS_REGION                    # AWS s3 리전 
                file_urls     = []

                for file in files:
                    s3_client.upload_fileobj(                                
                        file,
                        bucket_name,
                        'board_file/' + file.name,
                        ExtraArgs={
                            "ContentType": file.content_type
                        }
                    )
                    file_endpoint = file.name.replace(" ", "")
                    file_url = f'https://{bucket_name}.s3.{aws_region}.amazonaws.com/board_file/{file_endpoint}'
                    file_urls.append(file_url)
            
            with transaction.atomic():
                current_post = Post(
                    board_category_id = mother_post.board_category.id,
                    user_id           = request.user.id,
                    post_category_id  = post_category_id,
                    title             = title,
                    content           = content,
                    ip_address        = ip_address,
                    password          = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8'),
                    group_id          = mother_post.group_id,
                    group_order       = mother_post.group_order+1, # current_post의 group_order 지정
                    group_depth       = mother_post.group_depth+1, # current_post의 group_depth 지정
                    tag               = tag_names
                )

                # child_post_list의 group_order 업데이트
                if child_post_list:
                    child_post_list.update(
                        group_order=F('group_order')+1, 
                    ) 
                    
                # current_post가 child_post_list에 포함되어 group_order 값이 1 가산되는 것을 막기 위해 .save()를 .update() 이후에 배치함
                current_post.save()

                # 파일 URL 저장
                if files:
                    for file_url in file_urls:
                        fileupload = FileUpload(
                            post_id           = current_post.id,
                            path              = file_url
                        )
                        fileupload.save()               

            return JsonResponse({'message' : 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message' : 'KeyError'}, status = 400)
        except json.JSONDecodeError:
            return JsonResponse({'message' : 'JSONDecodeError'}, status = 400)
        except Post.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_POST_ID'}, status=401)