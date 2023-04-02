import boto3
import requests
import re
# 必要モジュールのインポート
import os
from dotenv import load_dotenv

import sys
sys.path.append('D:/User_Application/CMN00100_logging')
import CMN00100_logging as logging_

logging_.setting("CMN10200")
logging_.info("処理開始")

try:
    # .envファイルの内容を読み込見込む
    load_dotenv()

    DEBUG_=os.environ['DEBUG']

    AWS_HOST_ZONE_ID=os.environ['AWS_HOST_ZONE_ID']
    AWS_RECORD_NAME=os.environ['AWS_RECORD_NAME']
    if not DEBUG_:
        logging_.info("PROD")
        AWS_ACCESS_KEY=os.environ['AWS_ACCESS_KEY_DEV']
        AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY_DEV']  
    else:
        logging_.info("DEV")
        AWS_ACCESS_KEY=os.environ['AWS_ACCESS_KEY']
        AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY']

    AWS_CLOUDFRONT_DESTRIBUTION_ID=os.environ['AWS_CLOUDFRONT_DESTRIBUTION_ID']
    AWS_EC2_INSTANCE_ID=os.environ['AWS_EC2_INSTANCE_ID']

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
    ec2_public_dns = response['Reservations'][0]['Instances'][0]['PublicDnsName']
    cloudfront_domain_name = dist['Distribution']['DistributionConfig']['Origins']['Items'][0]['DomainName']

    
    if cloudfront_domain_name != ec2_public_dns:
        logging_.info("CloudFrontのオリジン情報を更新します。")
        logging_.info("更新前："+dist['Distribution']['DistributionConfig']['Origins']['Items'][0]['DomainName'])
        dist['Distribution']['DistributionConfig']['Origins']['Items'][0]['DomainName']=ec2_public_dns
         # 更新されたオリジン情報を表示
        logging_.info("更新後："+dist['Distribution']['DistributionConfig']['Origins']['Items'][0]['DomainName'])
        # CloudFrontディストリビューションを更新
        cloudfront_client.update_distribution(
            DistributionConfig=dist['Distribution']['DistributionConfig'],
            Id=AWS_CLOUDFRONT_DESTRIBUTION_ID,
            IfMatch=dist['ETag']
        )
        logging_.info("オリジン情報の更新完了")
    else:
        logging_.info("CloudFrontのオリジン情報は更新済みです。")
    logging_.info("正常終了")

except Exception as e:
    logging_.critical(e)
    logging_.info("異常終了")
