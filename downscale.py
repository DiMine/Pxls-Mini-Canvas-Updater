from PIL import Image
import numpy as np
import boto3
import io
from clueless import palettize_array, detemplatize, templatize, get_style_from_name, get_content
import asyncio
import json

# def lambda_handler(event, context):
#     asyncio.run(stuff())

async def stuff():
    s3_client = boto3.client('s3')
    info = json.loads(s3_client.get_object(
        Bucket='pogpega', 
        Key='info.json'
    )["Body"].read().decode('utf-8'))
    
    PALETTE = [f"#{color['value']}" for color in info["palette"]]
    
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
            Bucket='a.pogpega.farm',
            Key='avogadro.png',
            Body=output.getvalue(),
            ContentType='image/png'
        )
    with io.BytesIO() as output:
        templatized_image.save(output, format='PNG')
        s3_client.put_object(
            Bucket='a.pogpega.farm',
            Key='avogadro_detemp.png',
            Body=output.getvalue(),
            ContentType='image/png'
        )

asyncio.run(stuff())
