# 批量文件处理脚本
import os
import shutil
from pathlib import Path

def organize_downloads():
    """整理下载文件夹"""
    downloads = Path("~/Downloads").expanduser()
    
    # 文件类型分类
    categories = {
        "图片": [".jpg", ".png", ".gif"],
        "文档": [".pdf", ".doc", ".txt"],
        "视频": [".mp4", ".avi", ".mkv"],
        "压缩": [".zip", ".rar", ".7z"]
    }
    
    for file in downloads.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            for category, extensions in categories.items():
                if ext in extensions:
                    target_dir = downloads / category
                    target_dir.mkdir(exist_ok=True)
                    shutil.move(str(file), str(target_dir / file.name))
                    print(f"移动 {file.name} 到 {category}/")
                    break

organize_downloads()
