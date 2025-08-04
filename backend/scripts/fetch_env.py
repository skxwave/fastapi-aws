import boto3
import json

secret_name = "fastapi-dev"
region_name = "us-east-1"

client = boto3.client("secretsmanager", region_name=region_name)
response = client.get_secret_value(SecretId=secret_name)

secrets = json.loads(response["SecretString"])

with open(".env", "w") as f:
    for key, value in secrets.items():
        f.write(f"{key}={value}\n")
