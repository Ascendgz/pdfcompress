from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pdfcompress',
    version='0.1.0',
    author='Gary',
    description='Compress scanned PDF files while maintaining high quality',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/your-username/PDFcompress',
    packages=find_packages(),
    install_requires=[
        'pikepdf>=8.0.0',
        'Pillow>=10.0.0',
        'tqdm>=4.65.0',
    ],
    entry_points={
        'console_scripts': [
            'pdfcompress=pdfcompress.cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Utilities",
    ],
    keywords='pdf compress scan ebook',
)
