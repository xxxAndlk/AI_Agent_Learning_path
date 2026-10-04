import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional

class ModelVersionManager:
    """简单模型版本管理系统
    
    功能：
    - 模型注册和版本化
    - 模型切换和回滚
    - 元数据管理
    """
    def __init__(self, registry_path="./model_registry"):
        """
        参数:
            registry_path: 模型注册表路径
        """
        self.registry_path = registry_path
        self.metadata_file = os.path.join(registry_path, "registry.json")
        
        # 初始化注册表
        os.makedirs(registry_path, exist_ok=True)
        if not os.path.exists(self.metadata_file):
            self._save_registry({
                "models": {},
                "created_at": datetime.now().isoformat()
            })
    
    def _load_registry(self) -> Dict:
        """加载注册表"""
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict):
        """保存注册表"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def register_model(
        self,
        model_name: str,
        model_path: str,
        version: str = None,
        description: str = "",
        tags: List[str] = None,
        metrics: Dict = None
    ) -> str:
        """注册新模型版本
        
        参数:
            model_name: 模型名称
            model_path: 模型文件路径
            version: 版本号（默认自动生成）
            description: 版本描述
            tags: 标签列表
            metrics: 评估指标
        返回:
            版本号
        """
        registry = self._load_registry()
        
        # 自动生成版本号
        if version is None:
            if model_name not in registry["models"]:
                version = "v1.0.0"
            else:
                # 简单版本递增
                last_version = registry["models"][model_name]["versions"][-1]["version"]
                major, minor, patch = last_version.replace("v", "").split(".")
                version = f"v{major}.{minor}.{int(patch)+1}"
        
        # 创建版本目录
        version_dir = os.path.join(self.registry_path, model_name, version)
        os.makedirs(version_dir, exist_ok=True)
        
        # 复制模型文件
        if os.path.isfile(model_path):
            dest_path = os.path.join(version_dir, os.path.basename(model_path))
            shutil.copy2(model_path, dest_path)
        else:
            # 如果是目录，复制整个目录
            dest_path = os.path.join(version_dir, "model")
            shutil.copytree(model_path, dest_path, dirs_exist_ok=True)
        
        # 更新注册表
        if model_name not in registry["models"]:
            registry["models"][model_name] = {
                "versions": [],
                "production_version": None
            }
        
        version_info = {
            "version": version,
            "path": version_dir,
            "description": description,
            "tags": tags or [],
            "metrics": metrics or {},
            "created_at": datetime.now().isoformat(),
            "status": "staging"  # staging/production/deprecated
        }
        
        registry["models"][model_name]["versions"].append(version_info)
        self._save_registry(registry)
        
        print(f"模型已注册: {model_name}@{version}")
        return version
    
    def promote_to_production(self, model_name: str, version: str):
        """将模型提升为生产版本"""
        registry = self._load_registry()
        
        if model_name not in registry["models"]:
            raise ValueError(f"模型不存在: {model_name}")
        
        # 查找版本
        version_info = None
        for v in registry["models"][model_name]["versions"]:
            if v["version"] == version:
                version_info = v
                break
        
        if not version_info:
            raise ValueError(f"版本不存在: {version}")
        
        # 将之前的产品版本降级
        prev_prod = registry["models"][model_name]["production_version"]
        if prev_prod:
            for v in registry["models"][model_name]["versions"]:
                if v["version"] == prev_prod:
                    v["status"] = "archived"
                    break
        
        # 提升新版本
        version_info["status"] = "production"
        registry["models"][model_name]["production_version"] = version
        
        self._save_registry(registry)
        print(f"模型 {model_name}@{version} 已提升为生产版本")
    
    def get_model(self, model_name: str, version: str = None) -> str:
        """获取模型路径
        
        参数:
            model_name: 模型名称
            version: 版本号（默认使用生产版本）
        返回:
            模型路径
        """
        registry = self._load_registry()
        
        if model_name not in registry["models"]:
            raise ValueError(f"模型不存在: {model_name}")
        
        if version is None:
            version = registry["models"][model_name].get("production_version")
            if not version:
                raise ValueError(f"模型 {model_name} 没有生产版本")
        
        for v in registry["models"][model_name]["versions"]:
            if v["version"] == version:
                return v["path"]
        
        raise ValueError(f"版本不存在: {version}")
    
    def list_models(self) -> Dict:
        """列出所有模型"""
        registry = self._load_registry()
        return registry["models"]
    
    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict:
        """比较两个版本的指标"""
        registry = self._load_registry()
        
        v1_info = None
        v2_info = None
        
        for v in registry["models"][model_name]["versions"]:
            if v["version"] == version1:
                v1_info = v
            if v["version"] == version2:
                v2_info = v
        
        if not v1_info or not v2_info:
            raise ValueError("版本不存在")
        
        return {
            version1: v1_info["metrics"],
            version2: v2_info["metrics"]
        }

if __name__ == "__main__":
    # 使用示例
    manager = ModelVersionManager()
    
    # 假设有一个模型文件
    dummy_model_path = "dummy_model.pt"
    with open(dummy_model_path, 'w') as f:
        f.write("dummy model content")
    
    # 注册模型v1
    v1 = manager.register_model(
        model_name="text_classifier",
        model_path=dummy_model_path,
        description="初始版本",
        tags=["baseline", "bert"],
        metrics={"accuracy": 0.85, "f1": 0.83}
    )
    
    # 注册模型v2
    v2 = manager.register_model(
        model_name="text_classifier",
        model_path=dummy_model_path,
        description="优化版本",
        tags=["optimized", "bert"],
        metrics={"accuracy": 0.91, "f1": 0.90}
    )
    
    # 提升v2为生产版本
    manager.promote_to_production("text_classifier", v2)
    
    # 获取生产版本路径
    prod_path = manager.get_model("text_classifier")
    print(f"\n生产版本路径: {prod_path}")
    
    # 比较版本
    comparison = manager.compare_versions("text_classifier", v1, v2)
    print(f"\n版本对比:")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))
    
    # 清理
    os.remove(dummy_model_path)
