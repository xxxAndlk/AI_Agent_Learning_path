from pathlib import Path
from typing import Iterator

def find_large_files(
    directory: str, 
    size_mb: float = 10.0
) -> Iterator[tuple[Path, float]]:
    """
    查找大于指定大小的文件
    
    Args:
        directory: 搜索目录
        size_mb: 大小阈值（MB）
        
    Yields:
        (文件路径, 文件大小MB)
    """
    root = Path(directory)
    size_bytes = size_mb * 1024 * 1024
    
    for file_path in root.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size > size_bytes:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            yield (file_path, file_size_mb)
