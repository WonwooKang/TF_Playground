# -*- coding: utf-8 -*-
import os
import boto3
import traceback

if os.getenv("AWS_SAM_LOCAL"):
    session = boto3.Session(profile_name='ramaya')
else:
    session = boto3.Session()


def getS3File(key, bucket='api.ramaya.co.kr'):
    """
    임시 s3에서 파일 가져오기 - 임시버킷은 서비스명 필요

    :param key:
    :param serviceType:
    :return:
    """
    client = session.client("s3")
    # client = boto3.client(
    #     's3',
    #     # Hard coded strings as credentials, not recommended.
    #     aws_access_key_id='',
    #     aws_secret_access_key=''
    # )
    print(bucket + ' - S3 조회')
    print(key)
    try:
        obj = client.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        traceback.print_exc()
        return None

    return obj["Body"].read()

def upload(file, key, bucket):
    client = boto3.client("s3")



def upload_byte(data, key, bucket):
    client = boto3.client("s3")
