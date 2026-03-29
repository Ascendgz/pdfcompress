from PIL import Image
from typing import Tuple, Optional
import subprocess
import os


def detect_image_type(img: Image.Image) -> str:
    if img.mode == '1':
        return 'binary'
    elif img.mode in ('L', 'LA', 'P'):
        return 'grayscale'
    else:
        return 'color'


def downsample_image(img: Image.Image, target_dpi: int = 150) -> Image.Image:
    width, height = img.size
    
    scale_factor = target_dpi / 300.0
    
    if scale_factor >= 1:
        return img
    
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    if new_width < 100 or new_height < 100:
        return img
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def compress_jpeg(img: Image.Image, quality: int = 85) -> bytes:
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    return buffer.getvalue()


def compress_png(img: Image.Image, quality: int = 85) -> bytes:
    from io import BytesIO
    buffer = BytesIO()
    
    if img.mode == 'RGBA':
        img.save(buffer, format='PNG', optimize=True)
    elif img.mode in ('L', 'LA'):
        img.save(buffer, format='PNG', optimize=True)
    else:
        img.save(buffer, format='PNG', optimize=True)
    
    data = buffer.getvalue()
    
    if _pngquant_available():
        compressed = _compress_with_pngquant(data)
        if compressed:
            return compressed
    
    return data


def _pngquant_available() -> bool:
    try:
        result = subprocess.run(['pngquant', '--version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _compress_with_pngquant(data: bytes) -> Optional[bytes]:
    try:
        result = subprocess.run(
            ['pngquant', '--quality=65-85', '--speed=3', '-'],
            input=data,
            capture_output=True
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def compress_image(img: Image.Image, quality: int = 85, min_dpi: int = 600, 
                   downsample: bool = False, target_dpi: int = 150) -> Tuple[bytes, str, tuple]:
    if downsample:
        img = downsample_image(img, target_dpi)
    
    new_size = img.size
    
    img_type = detect_image_type(img)
    
    if img_type == 'binary':
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        return buffer.getvalue(), 'PNG', new_size
    elif img_type == 'grayscale':
        return compress_png(img, quality), 'PNG', new_size
    else:
        return compress_jpeg(img, quality), 'JPEG', new_size
