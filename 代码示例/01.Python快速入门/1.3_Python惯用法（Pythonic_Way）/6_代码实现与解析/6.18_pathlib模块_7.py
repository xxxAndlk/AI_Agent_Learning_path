from pathlib import Path
import json

# 场景1：配置文件读取
def load_config(config_dir: Path) -> dict:
    """加载配置文件"""
    config_file = config_dir / "config.json"
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    return json.loads(config_file.read_text())

# 场景2：项目结构检查
def check_project_structure(root: Path) -> list:
    """检查项目必需文件"""
    required = ["README.md", "src", "tests", "pyproject.toml"]
    missing = []
    for item in required:
        if not (root / item).exists():
            missing.append(item)
    return missing

# 场景3：批量文件处理
def process_markdown_files(folder: Path) -> None:
    """处理文件夹下所有markdown文件"""
    for md_file in folder.rglob("*.md"):
        # 读取内容
        content = md_file.read_text()
        # 简单的处理：添加标题
        new_content = f"# {md_file.stem}\n\n{content}"
        # 写回文件
        md_file.write_text(new_content)
        print(f"已处理: {md_file.relative_to(folder)}")

# 场景4：跨平台路径处理
def get_cache_dir() -> Path:
    """获取缓存目录，兼容不同操作系统"""
    import platform
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Caches"
    else:  # Linux
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "myapp"

# 使用示例
if __name__ == "__main__":
    # 当前目录下的config文件夹
    config_dir = Path(__file__).parent / "config"
    config = load_config(config_dir)
    
    # 检查项目结构
    project_root = Path(__file__).parent.parent
    missing = check_project_structure(project_root)
    if missing:
        print(f"缺少文件: {missing}")
