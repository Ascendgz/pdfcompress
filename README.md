# PDFcompress

一个高效的PDF压缩工具，专为扫描电子书PDF设计。通过降采样和JPEG质量压缩，在保持可读性的前提下大幅减小文件体积。

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd PDFcompress

# 安装（会创建全局命令）
pip install -e .
```

安装后，`pdfcompress` 命令会安装到Python的Scripts目录（如 `D:\miniconda3\Scripts\pdfcompress.exe`）。

### 依赖

- Python 3.8+
- pikepdf
- Pillow
- tqdm

## 快速开始

```bash
# 基本压缩（使用默认设置：150 DPI, JPEG质量85）
pdfcompress input.pdf

# 推荐设置（150 DPI, JPEG质量50，约66%压缩率）
pdfcompress input.pdf --downsample --target-dpi 150 -q 50

# 更高压缩（100 DPI, JPEG质量60，约81%压缩率）
pdfcompress input.pdf --downsample --target-dpi 100 -q 60
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入PDF文件或目录 | 必填 |
| `-o, --output` | 输出文件路径 | 自动添加 `_compressed` 后缀 |
| `-q, --quality` | JPEG压缩质量 (1-100) | 85 |
| `--downsample` | 启用降采样模式 | 否 |
| `--target-dpi` | 降采样目标DPI | 150 |
| `-v, --verbose` | 显示详细进度 | 否 |
| `-a, --aggressive` | 激进模式（重新压缩已压缩的图像） | 否 |
| `-h, --help` | 显示帮助信息 | - |

## 使用示例

### 单文件压缩

```bash
# 使用默认设置
pdfcompress ebook.pdf

# 指定输出路径
pdfcompress input.pdf -o output.pdf

# 显示详细进度
pdfcompress input.pdf --downsample --target-dpi 150 -q 50 -v
```

### 批量处理

```bash
# 处理当前目录所有PDF
pdfcompress *.pdf

# 处理整个文件夹
pdfcompress /path/to/folder/

# 批量处理并显示进度
pdfcompress *.pdf --downsample -q 50 -v
```

## 压缩效果对比

以测试文件 `明心数学资优教程-6年级卷.pdf`（218.98 MB，300 DPI）为例：

| 设置 | 文件大小 | 压缩率 | 适用场景 |
|------|---------|--------|---------|
| 原始 | 218.98 MB | - | - |
| 150 DPI, q=70 | 124.55 MB | 43% | 高质量阅读 |
| **150 DPI, q=50** | **73.60 MB** | **66%** | 平衡质量与体积 |
| 100 DPI, q=60 | 41.64 MB | 81% | 移动设备阅读 |
| 100 DPI, q=50 | ~35 MB | ~84% | 极限压缩 |

## DPI选择建议

| DPI | 像素密度 | 适用场景 |
|-----|---------|---------|
| 300 | 高清印刷级 | 打印、专业阅读 |
| 150 | 屏幕阅读级 | 电脑、平板阅读（推荐） |
| 100 | 移动设备级 | 手机阅读 |
| 72 | 网页级 | 快速浏览 |

## 工作原理

1. **图像提取**：从PDF中提取所有图像
2. **降采样**：将图像分辨率降低到目标DPI
3. **JPEG压缩**：使用指定质量重新压缩图像
4. **PDF重建**：将压缩后的图像写回PDF，保持页面布局不变

## 项目结构

```
PDFcompress/
├── pdfcompress/
│   ├── __init__.py          # 版本信息
│   ├── cli.py               # 命令行入口
│   ├── core.py              # 核心压缩逻辑
│   ├── pdf_handler.py       # PDF读写操作
│   ├── image_processor.py   # 图像压缩处理
│   └── utils.py             # 工具函数
├── docs/
│   └── superpowers/
│       └── specs/           # 设计文档
├── requirements.txt
├── setup.py
└── README.md
```

## 常见问题

### Q: 为什么基本压缩（无--downsample）没有效果？

A: 因为原图已经是压缩过的JPEG格式。需要使用 `--downsample` 进行降采样才能显著减小体积。

### Q: 压缩后页面显示只占四分之一？

A: 这是旧版本的问题，新版本已修复。请重新克隆或更新代码。

### Q: PowerShell显示乱码？

A: 运行以下命令设置编码：
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Q: 如何检查pdfcompress安装位置？

A: 运行：
```powershell
where.exe pdfcompress
```

## 许可证

MIT License
