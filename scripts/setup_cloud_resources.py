import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def setup_cloud_storage(bucket_name):
    """Sets up the cloud storage resources."""
    try:
        # Initialize a session using Amazon S3
        s3 = boto3.client('s3')

        # Create the bucket
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")

        # Set bucket policy for public access (if needed)
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
        print(f"Bucket policy set for '{bucket_name}'.")

    except NoCredentialsError:
        print("Error: AWS credentials not found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    BUCKET_NAME = os.getenv("CLOUD_STORAGE_BUCKET_NAME")
    if BUCKET_NAME:
        setup_cloud_storage(BUCKET_NAME)
    else:
        print("Error: Please set the CLOUD_STORAGE_BUCKET_NAME environment variable.")