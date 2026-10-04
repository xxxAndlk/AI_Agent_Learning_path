# -*- coding: utf-8 -*-
"""模型导出与格式转换演示：把"模拟权重矩阵"存成 json 再读回，看清模型文件 = 结构 + 参数。

第 1 段为纯标准库（json/os/tempfile），零依赖直接运行。
第 2、3 段为真实框架演示：pip install torch onnx
（未安装时打印中文提示并跳过，不影响第 1 段。）
"""
import json
import os
import tempfile

LINE = "-" * 46


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


# ---------- 第 1 段：纯标准库，零依赖 ----------

def make_toy_model():
    """造一个两层小"网络"：结构描述 + 各层参数。"""
    structure = {
        "model": "ToyNet",
        "layers": [
            {"name": "layer1", "type": "Linear", "in_features": 4, "out_features": 3},
            {"name": "layer2", "type": "Linear", "in_features": 3, "out_features": 2},
        ],
    }
    weights = {
        "layer1.weight": [[0.12, -0.50, 0.90, 0.03],
                          [0.77, 0.21, -0.44, 0.61],
                          [0.05, 0.33, 0.08, -0.27]],
        "layer1.bias": [0.01, -0.02, 0.03],
        "layer2.weight": [[0.50, -0.25, 0.75],
                          [0.10, 0.90, -0.30]],
        "layer2.bias": [0.00, 0.05],
    }
    return structure, weights


def forward(weights, x):
    """用参数表做前向计算：线性层 -> ReLU -> 线性层。"""
    h = x
    for name in ("layer1", "layer2"):
        w = weights[f"{name}.weight"]
        b = weights[f"{name}.bias"]
        h = [sum(wi * xi for wi, xi in zip(row, h)) + bi for row, bi in zip(w, b)]
        if name == "layer1":
            h = [max(0.0, v) for v in h]
    return h


def run_stdlib_demo():
    banner("第 1 段（纯标准库）：模型存成 json 再读回")
    structure, weights = make_toy_model()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "toy_model.json")
        blob = {"structure": structure, "parameters": weights}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(blob, f, ensure_ascii=False, indent=1)
        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        n_params = 0
        for v in weights.values():
            n_params += sum(len(r) for r in v) if isinstance(v[0], list) else len(v)
        same = loaded["parameters"] == weights
        print("导出文件字段:", list(loaded.keys()),
              "| 结构层数:", len(loaded["structure"]["layers"]))
        print(f"文件大小: {size} 字节 | 参数总数: {n_params}")
        print(f"读回校验: 参数{'完全一致' if same else '不一致(出错了!)'}")

        x = [1.0, 2.0, -1.0, 0.5]
        y0 = forward(weights, x)
        y1 = forward(loaded["parameters"], x)
        print(f"原参数前向输出: {[round(v, 4) for v in y0]}")
        print(f"读回后前向输出: {[round(v, 4) for v in y1]}")
        print("结论: 结构+参数读回来，模型原样复活。这就是一切模型文件格式的骨架。")


# ---------- 第 2 段：torch 的 state_dict ----------

def run_torch_demo():
    banner("第 2 段（torch）：state_dict 保存与加载")
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("[跳过] 本段需要 PyTorch，请先执行: pip install torch")
        return

    class ToyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = nn.Linear(4, 3)
            self.layer2 = nn.Linear(3, 2)

        def forward(self, t):
            return self.layer2(torch.relu(self.layer1(t)))

    model = ToyNet()
    state = model.state_dict()
    n_params = sum(p.numel() for p in state.values())
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "toy.pt")
        torch.save(state, path)
        size = os.path.getsize(path)
        model2 = ToyNet()
        model2.load_state_dict(torch.load(path))
        x = torch.tensor([[1.0, 2.0, -1.0, 0.5]])
        same = torch.allclose(model(x), model2(x))
        print(f"保存 {os.path.basename(path)} | {size} 字节 | 参数 {n_params} 个")
        print(f"加载后同输入前向输出一致: {same}")
        print("state_dict 就是讲义说的'行李清单'：部件名 -> 数值。")


# ---------- 第 3 段：ONNX 通用格式 ----------

def run_onnx_demo():
    banner("第 3 段（onnx）：导出通用格式并读回检查")
    try:
        import torch
        import torch.nn as nn
        import onnx
    except ImportError:
        print("[跳过] 本段需要 torch 与 onnx，请先执行: pip install torch onnx")
        return

    class ToyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = nn.Linear(4, 3)
            self.layer2 = nn.Linear(3, 2)

        def forward(self, t):
            return self.layer2(torch.relu(self.layer1(t)))

    model = ToyNet().eval()
    dummy = torch.randn(1, 4)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "toy.onnx")
        torch.onnx.export(model, dummy, path,
                          input_names=["input"], output_names=["output"])
        m = onnx.load(path)
        onnx.checker.check_model(m)
        size = os.path.getsize(path)
        names = [n.op_type for n in m.graph.node]
        print(f"导出 {os.path.basename(path)} | {size} 字节 | 已通过 onnx.checker 校验")
        print(f"计算图节点类型: {names}")
        print("结论: ONNX 把结构+参数翻成各家都认的通用写法，推理引擎据此加载运行。")


def main():
    print("第 01 课配套演示：模型导出与格式转换")
    run_stdlib_demo()   # 零依赖，必须成功
    run_torch_demo()    # 缺库自动跳过
    run_onnx_demo()     # 缺库自动跳过
    print("\n全部演示结束。")


if __name__ == "__main__":
    main()
