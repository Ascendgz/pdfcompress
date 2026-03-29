import os
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm

from .pdf_handler import (
    read_pdf, is_pdf_encrypted, extract_images_from_page, 
    extract_image_data, replace_image_in_pdf, save_pdf
)
from .image_processor import compress_image
from .utils import get_output_path, format_size, validate_pdf


def compress_pdf(
    input_path: str, 
    output_path: Optional[str] = None, 
    quality: int = 85, 
    min_dpi: int = 600, 
    verbose: bool = False,
    aggressive: bool = False, 
    downsample: bool = False, 
    target_dpi: int = 150
) -> dict:
    validate_pdf(input_path)
    
    if is_pdf_encrypted(input_path):
        raise ValueError(f"PDF is encrypted. Please decrypt first: {input_path}")
    
    if output_path is None:
        output_path = get_output_path(input_path)
    
    original_size = os.path.getsize(input_path)
    
    pdf = read_pdf(input_path)
    total_pages = len(pdf.pages)
    
    compressed_count = 0
    skipped_count = 0
    already_compressed_count = 0
    
    page_iter = tqdm(range(total_pages), desc="Compressing", disable=not verbose)
    
    for page_num in page_iter:
        page = pdf.pages[page_num]
        images = extract_images_from_page(page)
        
        for img_info in images:
            img_format = img_info.get('format', 'RAW')
            estimated_quality = img_info.get('estimated_quality', 100)
            
            should_compress = False
            effective_quality = quality
            
            if img_format == 'RAW' or img_format == 'PNG':
                should_compress = True
            elif img_format == 'JPEG':
                if aggressive or downsample:
                    should_compress = True
                    if aggressive:
                        effective_quality = min(quality, estimated_quality - 10)
                        effective_quality = max(effective_quality, 40)
                else:
                    already_compressed_count += 1
                    continue
            elif img_format in ('JPEG2000', 'JBIG2'):
                already_compressed_count += 1
                continue
            
            if not should_compress:
                continue
            
            try:
                img, _ = extract_image_data(img_info['xobj'])
                
                compressed_data, format_type, new_size = compress_image(
                    img, effective_quality, min_dpi, 
                    downsample=downsample, target_dpi=target_dpi
                )
                
                replace_image_in_pdf(
                    pdf, page_num, img_info['name'], 
                    compressed_data, format_type,
                    new_width=new_size[0] if downsample else None,
                    new_height=new_size[1] if downsample else None
                )
                compressed_count += 1
            except Exception as e:
                skipped_count += 1
                if verbose:
                    print(f"  Skipped image on page {page_num + 1}: {e}")
    
    if verbose:
        print(f"  Images already compressed: {already_compressed_count}")
        print(f"  Images recompressed: {compressed_count}")
        print(f"  Images skipped: {skipped_count}")
    
    save_pdf(pdf, output_path)
    
    compressed_size = os.path.getsize(output_path)
    reduction = (1 - compressed_size / original_size) * 100
    
    if compressed_size >= original_size:
        os.remove(output_path)
        print(f"  Warning: Compressed file larger than original. Original file kept.")
        return {
            'input': input_path,
            'output': None,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction': 0,
            'kept_original': True
        }
    
    return {
        'input': input_path,
        'output': output_path,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'reduction': reduction,
        'images_compressed': compressed_count,
        'images_skipped': skipped_count,
        'images_already_compressed': already_compressed_count
    }


def compress_batch(
    input_paths: List[str], 
    quality: int = 85, 
    min_dpi: int = 600, 
    verbose: bool = False,
    aggressive: bool = False, 
    downsample: bool = False,
    target_dpi: int = 150
) -> List[dict]:
    results = []
    
    for path in tqdm(input_paths, desc="Processing files"):
        try:
            result = compress_pdf(
                path, 
                quality=quality, 
                min_dpi=min_dpi, 
                verbose=verbose, 
                aggressive=aggressive,
                downsample=downsample, 
                target_dpi=target_dpi
            )
            results.append(result)
        except Exception as e:
            results.append({
                'input': path,
                'error': str(e)
            })
    
    return results


def expand_paths(paths: List[str]) -> List[str]:
    expanded = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            expanded.extend([str(f) for f in path.glob("*.pdf")])
        elif path.exists() and path.suffix.lower() == '.pdf':
            expanded.append(str(path))
        elif '*' in p:
            from glob import glob
            expanded.extend(glob(p))
    return expanded
