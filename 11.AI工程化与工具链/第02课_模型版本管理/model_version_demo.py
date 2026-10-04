"""model_version_demo.py —— 最小模型注册中心：版本登记 + 上线 + 回滚，纯标准库离线真跑。

运行：python model_version_demo.py（全程用临时目录，跑完自动清理）
（对应第 11 章第 02 课；12 章第 04 课 Dashboard 的"当前生产版本"即来自这种注册中心）
"""
import json
import tempfile
import time
from pathlib import Path

STATUS_CANDIDATE = "candidate"      # 候选：刚训练完，还没评估
STATUS_PRODUCTION = "production"    # 生产：线上正在用（同一时刻至多一个）
STATUS_ARCHIVED = "archived"        # 退役：被新版本替换或回滚下线


class ModelRegistry:
    """玩具注册中心：每个版本一个子目录（模型文件+配置），registry.json 记账。"""

    def __init__(self, root: Path):
        self.root = root
        self.manifest_path = root / "registry.json"
        self.root.mkdir(parents=True, exist_ok=True)
        if not self.manifest_path.exists():
            self._save({"versions": {}})

    def _load(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _save(self, manifest: dict) -> None:
        self.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    def register(self, version: str, experiment_run: str) -> Path:
        """登记新版本：模型文件 + 配置捆在一起存。experiment_run 链接回第01课的实验记录。"""
        vdir = self.root / version
        if vdir.exists():
            raise ValueError(f"版本 {version} 已存在，版本号不许复用")
        vdir.mkdir()
        (vdir / "model.bin").write_bytes(f"weights-of-{version}".encode("utf-8"))
        (vdir / "config.json").write_text(json.dumps({
            "model": "mini_rag_demo", "threshold": 0.5,
            "experiment_run": experiment_run,  # 溯源：这版怎么来的
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        m = self._load()
        m["versions"][version] = {"status": STATUS_CANDIDATE}
        self._save(m)
        print(f"[登记] v{version} -> candidate（含 model.bin + config.json）")
        return vdir

    def promote(self, version: str) -> None:
        """上线：production 标记挪到该版本，旧生产版本自动退役。"""
        m = self._load()
        if version not in m["versions"]:
            raise ValueError(f"版本 {version} 不存在")
        for v, info in m["versions"].items():
            if info["status"] == STATUS_PRODUCTION:
                info["status"] = STATUS_ARCHIVED
                print(f"[退役] v{v} -> archived")
        m["versions"][version]["status"] = STATUS_PRODUCTION
        self._save(m)
        print(f"[上线] v{version} -> production")

    def rollback(self, to_version: str) -> None:
        """回滚：把 production 指回去（改指针，不重训）。"""
        print("== 回滚 ==")
        self.promote(to_version)

    def current_production(self) -> str:
        m = self._load()
        for v, info in m["versions"].items():
            if info["status"] == STATUS_PRODUCTION:
                return v
        return "（无）"

    def show(self) -> None:
        m = self._load()
        print("当前账本:", json.dumps(m["versions"], ensure_ascii=False),
              "| 线上版本:", self.current_production())


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        reg = ModelRegistry(Path(td) / "registry")

        print("== 1) 登记两个版本 ==")
        reg.register("1", experiment_run="runs/20261004_093000_baseline")
        reg.register("2", experiment_run="runs/20261004_101500_lr_x10")

        print("\n== 2) v1 上线 ==")
        reg.promote("1")
        reg.show()

        print("\n== 3) v2 评估通过，上线替换 ==")
        reg.promote("2")
        reg.show()

        print("\n== 4) 线上出问题，回滚到 v1 ==")
        reg.rollback("1")
        reg.show()

        print("\n回滚不是重训：只是把 production 指针从 v2 挪回 v1，v2 留档待查。")


if __name__ == "__main__":
    main()
