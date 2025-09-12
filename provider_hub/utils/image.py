import base64
import mimetypes
from pathlib import Path
from typing import Union

def encode_image_to_base64(image_path: Union[str, Path]) -> str:
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"File is not a valid image: {image_path}")
    
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{encoded_string}"

def prepare_image_content(image_input: Union[str, Path]) -> dict:
    image_input = str(image_input)
    
    if image_input.startswith(('http://', 'https://')):
        return {"type": "image_url", "image_url": {"url": image_input}}
    else:
        base64_image = encode_image_to_base64(image_input)
        return {"type": "image_url", "image_url": {"url": base64_image}}