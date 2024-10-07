import boto3
from constants import AWS_SECRETS_MANAGER_NAME
import json

def get_secrets(region_name:str = "us-east-1") -> dict:
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    res = client.get_secret_value(SecretId=AWS_SECRETS_MANAGER_NAME)
    return json.loads(res["SecretString"])
