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
        info["height"], info["width"], 4
        )
    else:
        data = await get_content("https://pxls.space/boarddata", "bytes")
        arr = np.asarray(list(data), dtype=np.uint8).reshape(
        info["height"], info["width"]
        )
        arr = palettize_array(arr, PALETTE)
    
    del info
    del data
    
    # arr = detemplatize(arr, 80)
    image = Image.fromarray(arr)
    coeffs = [1.62443946e+01,  1.80493274e+01, -3.97085202e+02,  1.84857699e-13,
                6.78026906e+01,  3.39013453e+02,  1.19556707e-17,  2.24215247e-02]
    image = image.transform((148, 122), Image.PERSPECTIVE, coeffs, Image.NEAREST)
    beast = Image.open(io.BytesIO(s3_client.get_object(
        Bucket=BUCKET_PRIVATE,
        Key='MrBeast.png'
        )['Body'].read()))
    image.paste(beast, (0, 0), beast)
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
