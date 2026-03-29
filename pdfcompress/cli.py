import argparse
import sys
from pathlib import Path

from .core import compress_pdf, compress_batch, expand_paths
from .utils import format_size
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        prog='pdfcompress',
        description='Compress scanned PDF files while maintaining high quality'
    )
    parser.add_argument('input', nargs='+', help='Input PDF file(s) or directory')
    parser.add_argument('-o', '--output', help='Output file path (single file mode only)')
    parser.add_argument('-q', '--quality', type=int, default=85, 
                        help='JPEG quality (default: 85)')
    parser.add_argument('--dpi', type=int, default=600,
                        help='Minimum DPI to maintain (default: 600)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed progress')
    parser.add_argument('-a', '--aggressive', action='store_true',
                        help='Aggressive mode: recompress already compressed images with lower quality')
    parser.add_argument('--downsample', action='store_true',
                        help='Downsample images to reduce file size (reduces resolution)')
    parser.add_argument('--target-dpi', type=int, default=150,
                        help='Target DPI when downsampling (default: 150)')
    parser.add_argument('--version', action='version', 
                        version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    input_paths = expand_paths(args.input)
    
    if not input_paths:
        print("No PDF files found.")
        sys.exit(1)
    
    if len(input_paths) == 1 and args.output:
        result = compress_pdf(
            input_paths[0], 
            output_path=args.output,
            quality=args.quality,
            min_dpi=args.dpi,
            verbose=args.verbose,
            aggressive=args.aggressive,
            downsample=args.downsample,
            target_dpi=args.target_dpi
        )
        print_result(result)
    else:
        results = compress_batch(
            input_paths,
            quality=args.quality,
            min_dpi=args.dpi,
            verbose=args.verbose,
            aggressive=args.aggressive,
            downsample=args.downsample,
            target_dpi=args.target_dpi
        )
        print_summary(results)


def print_result(result):
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    if result.get('kept_original'):
        print(f"  Original: {format_size(result['original_size'])}")
        print(f"  Compressed would be: {format_size(result['compressed_size'])}")
        print(f"  Original file kept (compressed was larger)")
    else:
        print(f"  Original:   {format_size(result['original_size'])}")
        print(f"  Compressed: {format_size(result['compressed_size'])}")
        print(f"  Reduction:  {result['reduction']:.1f}%")


def print_summary(results):
    success = 0
    failed = 0
    total_saved = 0
    
    for r in results:
        if 'error' in r:
            print(f"[FAIL] {r['input']}: {r['error']}")
            failed += 1
        elif r.get('kept_original'):
            print(f"[SKIP] {r['input']}: compressed larger than original")
            success += 1
        else:
            saved = r['original_size'] - r['compressed_size']
            total_saved += saved
            print(f"[OK]   {Path(r['input']).name}: {format_size(r['original_size'])} -> "
                  f"{format_size(r['compressed_size'])} ({r['reduction']:.1f}% saved)")
            success += 1
    
    print()
    print(f"Processed: {success} succeeded, {failed} failed")
    if total_saved > 0:
        print(f"Total space saved: {format_size(total_saved)}")


if __name__ == '__main__':
    main()
