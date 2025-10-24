import boto3
from botocore.exceptions import ClientError
from decouple import config

def test_s3_connection():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_S3_REGION_NAME', default='us-west-2')
        )
        
        # Try to list buckets
        response = s3_client.list_buckets()
        print("✅ Connection successful!")
        print("Buckets:", [b['Name'] for b in response['Buckets']])
        
        # Try to upload a test file
        s3_client.put_object(
            Bucket=config('AWS_STORAGE_BUCKET_NAME'),
            Key='test1.txt',
            Body=b'Hello S3, testing S3!'
        )
        print("✅ Upload successful!")
        
    except ClientError as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_s3_connection()