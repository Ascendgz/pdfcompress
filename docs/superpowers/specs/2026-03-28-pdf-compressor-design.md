# PDF压缩工具设计文档

## 概述

一个命令行PDF压缩工具，专为扫描电子书PDF设计，目标压缩率50-80%，保持600 DPI以上高清质量。

## 技术栈

- Python 3.8+
- 核心库：pikepdf, Pillow, tqdm
- 系统依赖：pngquant, poppler

## 架构

```
CLI层 → 核心管道(PDFReader → ImageExtractor → ImageCompressor → PDFWriter) → 工具模块
```

## 模块设计

### cli.py
- 参数解析：输入文件/目录、输出路径、质量、DPI
- 批量处理支持
- 进度条显示

### core.py
- compress_pdf() 主入口
- compress_batch() 批量处理
- 协调各模块工作流

### pdf_handler.py
- read_pdf() 读取PDF结构
- extract_images() 提取图像
- rebuild_pdf() 重建PDF

### image_processor.py
- detect_image_type() 检测图像类型
- compress_jpeg() 彩色图像压缩(quality=85)
- compress_png() 灰度图像压缩

### utils.py
- 文件路径处理
- 临时文件清理
- 日志工具

## CLI接口

```bash
pdfcompress input.pdf                      # 基本用法
pdfcompress *.pdf                          # 批量处理
pdfcompress input.pdf -o output.pdf        # 指定输出
pdfcompress input.pdf -q 80                # 质量设置
pdfcompress input.pdf --dpi 600            # DPI设置
```

## 压缩策略

| 图像类型 | 压缩方式 | 参数 |
|---------|---------|------|
| 彩色 | JPEG | quality=85 |
| 灰度 | pngquant | 默认 |
| 二值 | 保持原样 | - |

## 错误处理

- 文件不存在/非PDF：报错退出
- PDF已加密：提示解密
- 压缩后更大：保留原文件，警告
- 中断：清理临时文件

## 项目结构

```
PDFcompress/
├── pdfcompress/
│   ├── __init__.py
│   ├── cli.py
│   ├── core.py
│   ├── pdf_handler.py
│   ├── image_processor.py
│   └── utils.py
├── requirements.txt
├── setup.py
└── README.md
```
