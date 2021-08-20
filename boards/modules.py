import boto3
import my_settings

def get_client_ip(self, request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_s3_client():
    s3_client = boto3.client(
        's3',                                                 # 사용할 서비스 이름
        aws_access_key_id = my_settings.ACESSS_KEY_ID,        # 액세스 ID
        aws_secret_access_key = my_settings.SECRET_ACCESS_KEY # 비밀 멕세스 키
    )
    return s3_client