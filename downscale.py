from PIL import Image
import numpy as np
import boto3
import io
from clueless import palettize_array, detemplatize, templatize, get_style_from_name, get_content
import asyncio
import json
import os

BUCKET_PRIVATE = os.environ['BUCKET_PRIVATE']
BUCKET_PUBLIC = os.environ['BUCKET_PUBLIC']
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

def lambda_handler(event, context):
    asyncio.run(stuff(event))

async def stuff(event):
    s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    info = json.loads(s3_client.get_object(
        Bucket=BUCKET_PRIVATE, 
        Key='info.json'
    )["Body"].read().decode('utf-8'))

    PALETTE = [f"#{color['value']}" for color in info["palette"]]
    
    if 'url' in event:
        data = await get_content(event['url'], 'image')
        data = Image.open(io.BytesIO(data))
        data = data.getdata()
        data = np.array(data)
        arr = np.asarray(list(data), dtype=np.uint8).reshape(
        info["width"], info["height"], 4
        )
    else:
        data = await get_content("https://pxls.space/boarddata", "bytes")
        arr = np.asarray(list(data), dtype=np.uint8).reshape(
        info["width"], info["height"]
        )
        arr = palettize_array(arr, PALETTE)

    arr = detemplatize(arr, 80)
    image = Image.fromarray(arr, mode='RGBA')
    style = get_style_from_name('custom')
    arr = templatize(style, image, PALETTE)
    templatized_image = Image.fromarray(arr, mode='RGBA')

    with io.BytesIO() as output:
        image.save(output, format='PNG')
        s3_client.put_object(
            Bucket=BUCKET_PUBLIC,
            Key='avogadro_detemp.png',
            Body=output.getvalue(),
            ContentType='image/png'
        )
    with io.BytesIO() as output:
        templatized_image.save(output, format='PNG')
        s3_client.put_object(
            Bucket=BUCKET_PUBLIC,
            Key='avogadro.png',
            Body=output.getvalue(),
            ContentType='image/png'
        )

asyncio.run(stuff({'url': 'https://cdn.discordapp.com/attachments/1197717552361648180/1239576410247663636/board.png?ex=66436cfe&is=66421b7e&hm=fd944a1faff843d763fc41e1753db5652fe959bbccab74b97a122af1298f9a03&'}))
