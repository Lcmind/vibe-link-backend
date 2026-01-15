"""ImgBB image hosting service."""

import base64
import httpx
from app.core.config import settings


async def upload_to_imgbb(image_path: str) -> str:
    """
    Upload image to ImgBB for permanent hosting.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Public URL of the uploaded image
        
    Raises:
        Exception: If upload fails
    """
    with open(image_path, 'rb') as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': settings.imgbb_key,
                'image': image_data,
            },
            timeout=30.0
        )
    
    result = response.json()
    
    if not result.get('success'):
        raise Exception(f"ImgBB upload failed: {result}")
    
    return result['data']['url']
