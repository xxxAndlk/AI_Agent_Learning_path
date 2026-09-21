#!/usr/bin/env python3
"""批量重命名工具 - 类似Go的CLI工具"""

import os
import sys
from pathlib import Path

def batch_rename(pattern, replacement, directory="."):
    """批量重命名文件"""
    for filepath in Path(directory).glob(pattern):
        new_name = filepath.name.replace(pattern, replacement)
        new_path = filepath.parent / new_name
        filepath.rename(new_path)
        print(f"Renamed: {filepath} -> {new_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rename.py <pattern> <replacement>")
        sys.exit(1)
    
    batch_rename(sys.argv[1], sys.argv[2])
