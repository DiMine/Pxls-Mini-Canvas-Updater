import json
from clueless import get_content
import boto3
import asyncio
import os

BUCKET_PRIVATE = os.environ['BUCKET_PRIVATE']

def lambda_handler(event, context):
    asyncio.run(stuff())
    

async def stuff():
    info = await get_content("https://pxls.space/info", "json")
    saved_info = {
        "width": info["width"],
        "height": info["height"],
        "palette": info["palette"]
    }
    
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=BUCKET_PRIVATE,
        Key='info.json',
        Body=json.dumps(saved_info),
        ContentType='application/json'
        )