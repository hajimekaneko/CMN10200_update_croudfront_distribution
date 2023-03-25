import boto3
import requests
import re
# 必要モジュールのインポート
import os
from dotenv import load_dotenv

# .envファイルの内容を読み込見込む
load_dotenv()

DEBUG_=os.environ['DEBUG']

AWS_HOST_ZONE_ID=os.environ['AWS_HOST_ZONE_ID']
AWS_RECORD_NAME=os.environ['AWS_RECORD_NAME']
if not DEBUG_:
    AWS_ACCESS_KEY=os.environ['AWS_ACCESS_KEY_DEV']
    AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY_DEV']  
    print("PROD")
else:
    AWS_ACCESS_KEY=os.environ['AWS_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY']
    print("DEV")

AWS_CLOUDFRONT_DESTRIBUTION_ID='E2GBZVMGSQ573N'

# EC2インスタンスのID
AWS_EC2_INSTANCE_ID = 'i-019498845526f470c'

boto3_session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
cloudfront_client = boto3_session.client('cloudfront')
ec2_client = boto3_session.client('ec2')

# Distribution ID を指定して Distribution を取得
dist = cloudfront_client.get_distribution(Id=AWS_CLOUDFRONT_DESTRIBUTION_ID)

# Distribution Config から Origin を取得
origins = dist['Distribution']['DistributionConfig']['Origins']['Items']

# Origin から Domain Name を取得
origin_domain = origins[0]['DomainName']
# Origin から Origin ID を取得
origin_id = origins[0]['Id']

# DescribeInstances APIを使用して、EC2インスタンスの情報を取得
response = ec2_client.describe_instances(InstanceIds=[AWS_EC2_INSTANCE_ID])

# インスタンス情報からElastic IPアドレスを取得
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
public_dns = response['Reservations'][0]['Instances'][0]['PublicDnsName']


print(dist['Distribution']['DistributionConfig']['Origins']['Items'][0])

# オリジン情報を更新
dist['Distribution']['DistributionConfig']['Origins']['Items'][0]['DomainName']=public_dns

# 更新されたオリジン情報を表示
print(dist['Distribution']['DistributionConfig']['Origins']['Items'][0])

# CloudFrontディストリビューションを更新
cloudfront_client.update_distribution(
    DistributionConfig=dist['Distribution']['DistributionConfig'],
    Id=AWS_CLOUDFRONT_DESTRIBUTION_ID,
    IfMatch=dist['ETag']
)

print(public_dns)
