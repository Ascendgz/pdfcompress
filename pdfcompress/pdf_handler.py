import pikepdf
from typing import List, Dict, Tuple, Optional
from PIL import Image
import io
import zlib


def read_pdf(path: str) -> pikepdf.Pdf:
    return pikepdf.open(path)


def is_pdf_encrypted(path: str) -> bool:
    try:
        with pikepdf.open(path) as pdf:
            return False
    except pikepdf.PasswordError:
        return True


def get_image_format(xobj: pikepdf.Object) -> str:
    if '/Filter' not in xobj:
        return 'RAW'
    
    filters = xobj['/Filter']
    if not isinstance(filters, list):
        filters = [filters]
    
    for f in filters:
        f_str = str(f)
        if f_str == '/DCTDecode':
            return 'JPEG'
        elif f_str == '/JPXDecode':
            return 'JPEG2000'
        elif f_str == '/FlateDecode':
            return 'PNG'
        elif f_str == '/JBIG2Decode':
            return 'JBIG2'
        elif f_str == '/CCITTFaxDecode':
            return 'TIFF'
    
    return 'RAW'


def estimate_jpeg_quality(xobj: pikepdf.Object) -> int:
    raw_data = bytes(xobj.read_raw_bytes())
    size = len(raw_data)
    width = int(xobj.get('/Width', 1))
    height = int(xobj.get('/Height', 1))
    
    bytes_per_pixel = size / (width * height)
    
    if bytes_per_pixel > 0.5:
        return 95
    elif bytes_per_pixel > 0.3:
        return 85
    elif bytes_per_pixel > 0.15:
        return 75
    else:
        return 60


def extract_images_from_page(page: pikepdf.Page) -> List[Dict]:
    images = []
    
    if '/Resources' not in page:
        return images
    
    resources = page['/Resources']
    if '/XObject' not in resources:
        return images
    
    xobjects = resources['/XObject']
    
    for name, xobj in xobjects.items():
        if xobj.get('/Subtype') == '/Image':
            img_format = get_image_format(xobj)
            estimated_quality = estimate_jpeg_quality(xobj) if img_format == 'JPEG' else 100
            
            images.append({
                'name': str(name),
                'xobj': xobj,
                'width': int(xobj.get('/Width', 0)),
                'height': int(xobj.get('/Height', 0)),
                'colorspace': str(xobj.get('/ColorSpace', '')),
                'bits_per_component': int(xobj.get('/BitsPerComponent', 8)),
                'format': img_format,
                'estimated_quality': estimated_quality,
            })
    
    return images


def extract_image_data(xobj: pikepdf.Object) -> Tuple[Image.Image, str]:
    width = int(xobj['/Width'])
    height = int(xobj['/Height'])
    colorspace = str(xobj.get('/ColorSpace', '/DeviceRGB'))
    bpc = int(xobj.get('/BitsPerComponent', 8))
    
    raw_data = bytes(xobj.read_raw_bytes())
    
    if '/Filter' in xobj:
        filters = xobj['/Filter']
        if not isinstance(filters, list):
            filters = [filters]
        
        for f in filters:
            if str(f) == '/FlateDecode':
                raw_data = zlib.decompress(raw_data)
            elif str(f) == '/DCTDecode':
                return Image.open(io.BytesIO(raw_data)), 'JPEG'
            elif str(f) == '/JPXDecode':
                return Image.open(io.BytesIO(raw_data)), 'JPEG2000'
    
    if colorspace == '/DeviceGray':
        mode = 'L'
    elif colorspace == '/DeviceCMYK':
        mode = 'CMYK'
    else:
        mode = 'RGB'
    
    img = Image.frombytes(mode, (width, height), raw_data)
    return img, 'RAW'


def replace_image_in_pdf(pdf: pikepdf.Pdf, page_num: int, image_name: str, 
                          new_data: bytes, format: str, 
                          new_width: Optional[int] = None, 
                          new_height: Optional[int] = None) -> None:
    page = pdf.pages[page_num]
    
    if '/Resources' not in page:
        return
    
    resources = page['/Resources']
    if '/XObject' not in resources:
        return
    
    xobjects = resources['/XObject']
    
    for name, xobj in xobjects.items():
        if str(name) == image_name:
            if format == 'JPEG':
                xobj.write(new_data, filter=pikepdf.Name.DCTDecode)
            else:
                xobj.write(new_data, filter=pikepdf.Name.FlateDecode)
            
            if new_width is not None:
                xobj['/Width'] = new_width
            if new_height is not None:
                xobj['/Height'] = new_height
            break


def save_pdf(pdf: pikepdf.Pdf, output_path: str) -> None:
    pdf.save(output_path)
    pdf.close()
