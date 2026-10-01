#!/usr/bin/env python3
"""
文件搜索CLI工具
支持按名称、大小、时间搜索
"""
import argparse
from pathlib import Path
from datetime import datetime
from typing import Iterator

def search_files(
    directory: str,
    name_pattern: str = "*",
    min_size: int = 0,
    max_size: int = float('inf'),
    days: int | None = None
) -> Iterator[Path]:
    """搜索文件"""
    root = Path(directory)
    
    for path in root.rglob(name_pattern):
        if not path.is_file():
            continue
            
        size = path.stat().st_size
        if not min_size <= size <= max_size:
            continue
            
        if days is not None:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if (datetime.now() - mtime).days > days:
                continue
                
        yield path

def main():
    parser = argparse.ArgumentParser(description="文件搜索工具")
    parser.add_argument("directory", help="搜索目录")
    parser.add_argument("-n", "--name", default="*", help="文件名模式")
    parser.add_argument("--min-size", type=int, default=0, help="最小大小(bytes)")
    parser.add_argument("--max-size", type=int, default=float('inf'), help="最大大小")
    parser.add_argument("--days", type=int, help="最近修改天数")
    
    args = parser.parse_args()
    
    for path in search_files(
        args.directory,
        args.name,
        args.min_size,
        args.max_size,
        args.days
    ):
        print(path)

if __name__ == "__main__":
    main()
