from os import path
import unittest
import bcrypt
import jwt
import json

from django.test   import Client, TestCase
from unittest.mock import MagicMock, patch

from users.models  import User
from .models       import (
    BoardCategory, Post, PostCategory,
    FileUpload
)    
import my_settings

class BoardWriteTest(TestCase): 
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
            
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()

    def test_board_write_key_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            # "board_category_id": 1,
            "post_category_id": 1,
            "title": "문의 드립니다.",
            "content": "상품 배송 예정일은 언제인가요?",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의"
        }

        response = c.post('/boards/board-write', {"json":json.dumps(body)}, **header) 
        self.assertContains(response=response, text='KeyError', status_code=400)

    def test_board_write_json_decodeError(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "board_category_id": 1,
            "post_category_id": 1,
            "title": "문의 드립니다.",
            "content": "상품 배송 예정일은 언제인가요?",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의",
        }

        response = c.post('/boards/board-write', {"json":body}, **header)
        self.assertContains(response=response, text='JSONDecodeError', status_code=400)

    @patch('boards.views.create_s3_client')
    def test_board_write_success(self, mocked_s3_client):
        class FakeResponse:
            def json(self):
                return None

        mocked_s3_client.upload_fileobj = MagicMock(return_value = FakeResponse())

        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "board_category_id": 1,
            "post_category_id": 1,
            "title": "문의 드립니다.",
            "content": "상품 배송 예정일은 언제인가요?",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의",
        }

        with open('/Users/younghun/Downloads/IMG_1749.JPG', 'rb') as myfile1, open('/Users/younghun/Downloads/얼평.jpeg', 'rb') as myfile2 :
            response = c.post('/boards/board-write', {"json":json.dumps(body), "filename": [myfile1, myfile2]}, **header)     
        print('file_uploads_object_count_write :', FileUpload.objects.count())

        self.assertContains(response=response, text='SUCCESS', status_code=200)

class BoardRewriteTest(TestCase): 
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )
        password          = 'gns7201ok!'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        Post.objects.create(
            id                = 1,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 1,
            title             = "문의 드립니다.",
            content           = "상품 배송 예정일은 언제인가요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1,
            tag               = '배송날짜, 배송문의'
        )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()

    def test_board_rewrite_key_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            # "title": "문의 드립니다. real 문의",
            "content": "상품 배송 예정일은 언제인가요????????",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의, 재입고문의"
        }

        response = c.post('/boards/board-rewrite', {"json":json.dumps(body)}, **header) 
        self.assertContains(response=response, text='KeyError', status_code=400)

    def test_board_rewrite_json_decodeError(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "title": "문의 드립니다. real 문의",
            "content": "상품 배송 예정일은 언제인가요????????",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의, 재입고문의"
        }

        response = c.post('/boards/board-rewrite', {"json":body}, **header)
        self.assertContains(response=response, text='JSONDecodeError', status_code=400)

    def test_board_rewrite_invalid_password_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "title": "문의 드립니다. real 문의",
            "content": "상품 배송 예정일은 언제인가요????????",
            "password": "1234",
            "tag_names": "배송날짜, 배송문의, 재입고문의"
        }

        response = c.post('/boards/board-rewrite', {'json' : json.dumps(body)}, **header)
        self.assertContains(response=response, text='INVALID_POST_PASSWORD', status_code=401)

    def test_board_rewrite_invalid_post_id_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 2,
            "title": "문의 드립니다. real 문의",
            "content": "상품 배송 예정일은 언제인가요????????",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의, 재입고문의"
        }

        response = c.post('/boards/board-rewrite', {'json' : json.dumps(body)}, **header)
        self.assertContains(response=response, text='INVALID_POST_ID', status_code=401)

    @patch('boards.views.create_s3_client')
    def test_board_rewrite_success(self, mocked_s3_client):
        class FakeResponse:
            def json(self):
                return None

        mocked_s3_client.upload_fileobj = MagicMock(return_value = FakeResponse())

        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "title": "문의 드립니다. real 문의",
            "content": "상품 배송 예정일은 언제인가요????????",
            "password": "gns7201ok!",
            "tag_names": "배송날짜, 배송문의, 재입고문의"
        }

        with open('/Users/younghun/Downloads/IMG_1749.JPG', 'rb') as myfile1, open('/Users/younghun/Downloads/얼평.jpeg', 'rb') as myfile2 :
            response = c.post('/boards/board-rewrite', {'json' : json.dumps(body), 'filename' : myfile1}, **header)
        print('file_uploads_object_count_rewrite :', FileUpload.objects.count())

        self.assertContains(response=response, text='SUCCESS', status_code=200)

class BoardDeleteTest(TestCase): 
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )
        password          = 'gns7201ok!'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        Post.objects.create(
            id                = 1,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 1,
            title             = "문의 드립니다.",
            content           = "상품 배송 예정일은 언제인가요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1,
            tag               = '배송날짜, 배송문의'
        )

        FileUpload.objects.create(
            post_id  = 1,
            path     = 'picture.jpg'
        )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()
        FileUpload.objects.all().delete()

    def test_board_rewrite_key_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            # "post_id": 1,
            "password": "gns7201ok!",
        }

        response = c.post('/boards/board-delete', json.dumps(body), content_type='applications/json', **header) 
        self.assertContains(response=response, text='KeyError', status_code=400)

    def test_board_rewrite_json_decodeError(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "password": "gns7201ok!",
        }

        response = c.post('/boards/board-delete', body, content_type='applications/json', **header)
        self.assertContains(response=response, text='JSONDecodeError', status_code=400)

    def test_board_delete_invalid_password_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "password":'1234'
        }

        response = c.post('/boards/board-delete', json.dumps(body), content_type='applications/json', **header)

        self.assertContains(response=response, text='INVALID_POST_PASSWORD', status_code=401)

    def test_board_delete_invalid_post_id_error(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 2,
            "password": "gns7201ok!",
        }

        response = c.post('/boards/board-delete', json.dumps(body), content_type='applications/json', **header)

        self.assertContains(response=response, text='INVALID_POST_ID', status_code=401)

    @patch('boards.views.create_s3_client')
    def test_board_delete_success(self, mocked_s3_client):
        class FakeResponse:
            def json(self):
                return None

        mocked_s3_client.upload_fileobj = MagicMock(return_value = FakeResponse())

        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "password": "gns7201ok!",
        }

        response = c.post('/boards/board-delete', json.dumps(body), content_type='applications/json', **header)
        print('file_uploads_object_count_delete :', FileUpload.objects.count())

        if not Post.objects.filter(id=1).exists():
            self.assertContains(response=response, text='SUCCESS', status_code=200)

class BoardListTest(TestCase):
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )
        password          = 'gns7201ok!'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        Post.objects.create(
            id                = 1,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 1,
            title             = "문의 드립니다.",
            content           = "상품 배송 예정일은 언제인가요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1,
            tag               = '배송날짜, 배송문의'
        )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()

    def test_board_list_value_error(self):
        c        = Client()
        post     = Post.objects.filter(id=1).first()

        param    = {
            "page" : 'a'
        }

        response = c.get('/boards/board-list', param)

        self.assertContains(response=response, text='ENTER page_number', status_code=400)

    def test_board_list_success(self):
        c        = Client()
        post     = Post.objects.filter(id=1).first()

        param    = {
            "page" : 1
        }

        response = c.get('/boards/board-list', param)

        result = [{
            'id'            : post.id,
            'title'         : post.title,
            'post_category' : post.post_category.name,
            'writer'        : post.user.nickname,
            'final_updated' : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'views'         : post.views,
            'group_id'      : post.group_id,
            'group_order'   : post.group_order,
            'group_depth'   : post.group_depth
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    "result"   : result
                }
            )

class BoardDetailTest(TestCase):
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )
        password          = 'gns7201ok!'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        Post.objects.create(
            id                = 1,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 1,
            title             = "문의 드립니다.",
            content           = "상품 배송 예정일은 언제인가요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1,
            tag               = '배송날짜, 배송문의'
        )
        FileUpload.objects.create(
            post_id  = 1,
            path     = 'picture.jpg'
        )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()
        FileUpload.objects.all().delete()

    def test_board_detail_invalid_post_id(self):
        c        = Client()

        response = c.get('/boards/3')

        self.assertContains(response=response, text='INVALID_POST_ID', status_code=401)

    def test_board_detail_success(self):
        c        = Client()
        post     = Post.objects.filter(id=1).first()

        response = c.get('/boards/1')

        post_info =[{
            "post_category" : post.post_category.name,
            "writer"        : post.user.nickname,
            "title"         : post.title,
            "content"       : post.content,
            "ip_address"    : post.ip_address,
            "tag"           : post.tag.replace(" ", "").split(",") if post.tag else None,
            "updated_at"    : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "file_uploads"  : [str(obj.path).split('/board_file/')[-1] for obj in post.fileupload_set.all()] if post.fileupload_set.all() else None
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                {
                    "result"   : post_info
                }
            )

class BoardReplyTest(TestCase):
    def setUp(self):
        password          = '1234'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        User.objects.create(
            id            = 1,
            name          = 'fcfargo',
            email         = 'test@gmail.com',
            password      = hashed_password,
            nickname      = '침착맨'
           )
        BoardCategory.objects.create(
            id            = 1,
            name          = '고객 문의 게시판',
           )
        names = ['일반 글', '답글']
        for i in range(len(names)):
            PostCategory.objects.create(
                id        = i+1,
                name      = names[i],
            )
        password          = 'gns7201ok!'
        hashed_password   = bcrypt.hashpw(
                password.encode('UTF-8'), bcrypt.gensalt()
            ).decode('UTF-8')
        Post.objects.create(
            id                = 1,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 1,
            title             = "문의 드립니다.",
            content           = "상품 배송 예정일은 언제인가요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1    
        )
        Post.objects.create(
            id                = 2,
            board_category_id = 1,
            user_id           = 1,
            post_category_id  = 2,
            title             = "질문 드립니다",
            content           = "왜 쿠폰 이벤트 안하는건가요? 언제하나요? 거짓말이었나요?",
            ip_address        = '127.0.0.1',
            password          = hashed_password,  
            group_id          = 1,
            group_order       = 1,
            group_depth       = 1,
            tag               = '배송날짜, 배송문의'
        )

    def tearDown(self):
        User.objects.filter(name='fcfargo').delete()
        Post.objects.all().delete()
        BoardCategory.objects.all().delete()
        PostCategory.objects.all().delete()

    def test_board_reply_invalid_post_id(self):
        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 3,
            "title": "가입 기념 쿠폰을 받고 싶은신가요",
            "content": "가입 쿠폰은 프리미엄 회원에게만 지급됩니다. 이번 기회에 회원 등급을 업그레이드해보세요!",
            "password": "gns7201ok!"
        }
        response = c.post('/boards/board-reply', {'json': json.dumps(body)}, **header)

        self.assertContains(response=response, text='INVALID_POST_ID', status_code=401)

    @patch('boards.views.create_s3_client')
    def test_board_reply_success(self, mocked_s3_client):
        class FakeResponse:
            def json(self):
                return None

        mocked_s3_client.upload_fileobj = MagicMock(return_value = FakeResponse())

        c        = Client()
        user     = User.objects.filter(name='fcfargo').first()
        token    = jwt.encode({"user_id" : user.id}, my_settings.SECRET['secret'], algorithm="HS256")
        header   = {'HTTP_Authorization' : token} 
        body     = {
            "post_id": 1,
            "title": "가입 기념 쿠폰을 받고 싶은신가요",
            "content": "가입 쿠폰은 프리미엄 회원에게만 지급됩니다. 이번 기회에 회원 등급을 업그레이드해보세요!",
            "password": "gns7201ok!"
        }
        with open('/Users/younghun/Downloads/IMG_1749.JPG', 'rb') as myfile1, open('/Users/younghun/Downloads/얼평.jpeg', 'rb') as myfile2 :
            response = c.post('/boards/board-reply', {'json': json.dumps(body), 'filename':[myfile1, myfile2]}, **header)
        
        print('file_uploads_object_count_reply :', FileUpload.objects.count())
        current_post = Post.objects.filter(id=3).first()
        child_post   = Post.objects.filter(id=2).first()      

        if current_post.group_order == child_post.group_order -1:
            self.assertContains(response=response, text='SUCCESS', status_code=200)

if __name__=='__main__':
    unittest.main()