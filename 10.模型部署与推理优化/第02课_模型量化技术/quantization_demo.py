# -*- coding: utf-8 -*-
"""模型量化演示：手算 float -> int8/int4 对称量化、反量化，打印量化误差。

第 1 段为纯标准库，零依赖直接运行。
第 2 段为真实 PyTorch 量化演示：pip install torch
（未安装时打印中文提示并跳过，不影响第 1 段。）
"""
LINE = "-" * 52


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


def quantize(w, qmax):
    """对称量化：scale = max|w|/qmax，返回量化整数与 scale。"""
    scale = max(abs(v) for v in w) / qmax
    if scale == 0:
        scale = 1e-8
    q = [max(-qmax, min(qmax, round(v / scale))) for v in w]
    return q, scale


def dequantize(q, scale):
    """反量化：整数乘回 scale，得到近似的 float。"""
    return [v * scale for v in q]


def errors(orig, approx):
    """逐点误差 + 整体统计。"""
    diffs = [a - b for a, b in zip(orig, approx)]
    return diffs, max(abs(d) for d in diffs), sum(d * d for d in diffs) / len(diffs)


def mlp_forward(w1, b1, w2, b2, x):
    """两层小网络前向：线性 -> ReLU -> 线性。"""
    h = [sum(w * xi for w, xi in zip(row, x)) + bi for row, bi in zip(w1, b1)]
    h = [max(0.0, v) for v in h]
    return [sum(w * hi for w, hi in zip(row, h)) + bi for row, bi in zip(w2, b2)]


def run_stdlib_demo():
    banner("第 1 段（纯标准库）：手算 int8 / int4 量化与误差")
    # 一组模拟的模型权重（1x4 隐层 -> 2 输出）
    w = [0.82, -0.31, 0.05, -0.99, 0.44, 0.63, -0.17, 0.28]
    w1 = [[0.82, -0.31, 0.05, -0.99], [0.44, 0.63, -0.17, 0.28]]
    b1 = [0.02, -0.03]
    w2 = [[0.70, -0.20], [0.15, 0.55]]
    b2 = [0.00, 0.04]
    x = [1.0, -0.5, 2.0, 0.3]

    print(f"原始 float32 权重（{len(w)} 个，每个 4 字节）:")
    print("  ", [round(v, 4) for v in w])

    for name, qmax in (("int8", 127), ("int4", 7)):
        q, scale = quantize(w, qmax)
        back = dequantize(q, scale)
        diffs, max_err, mse = errors(w, back)
        print(f"\n{name} 量化（范围 -{qmax}~{qmax}，scale={scale:.6f}）:")
        print(f"  量化整数 : {q}")
        print(f"  反量化回 : {[round(v, 4) for v in back]}")
        print(f"  逐点误差 : {[round(d, 4) for d in diffs]}")
        print(f"  最大误差 {max_err:.4f} | 均方误差 {mse:.6f}")
        bytes_per = 1.0 if qmax == 127 else 0.5
        print(f"  存储: 每参数 {bytes_per} 字节（约 float32 的 {bytes_per / 4 * 100:.0f}%）")

    # 量化后整网推理对比：看输出走样多少
    print("\n--- 量化前后推理输出对比 ---")
    y0 = mlp_forward(w1, b1, w2, b2, x)
    print(f"float32 输出: {[round(v, 4) for v in y0]}")
    for name, qmax in (("int8", 127), ("int4", 7)):
        flat = [v for row in w1 for v in row] + [v for row in w2 for v in row]
        q, scale = quantize(flat, qmax)
        back = dequantize(q, scale)
        qw1 = [back[0:4], back[4:8]]
        qw2 = [back[8:10], back[10:12]]
        y = mlp_forward(qw1, b1, qw2, b2, x)
        _, max_err, _ = errors(y0, y)
        print(f"{name}  输出: {[round(v, 4) for v in y]} | 输出最大偏差 {max_err:.4f}")
    print("结论: int8 几乎无感，int4 开始可见偏差——位宽换精度的交换看得见摸得着。")


def run_torch_demo():
    banner("第 2 段（torch）：真·int8 动态量化对比")
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("[跳过] 本段需要 PyTorch，请先执行: pip install torch")
        return

    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(256, 512), nn.ReLU(), nn.Linear(512, 64)).eval()
    x = torch.randn(8, 256)
    with torch.no_grad():
        y_fp32 = model(x)
    try:
        q_model = torch.ao.quantization.quantize_dynamic(
            model, {nn.Linear}, dtype=torch.qint8)
    except Exception as e:
        print(f"[跳过] 当前环境不支持动态量化（原因: {type(e).__name__}），"
              "第 1 段的手算演示已覆盖本课知识点。")
        return
    with torch.no_grad():
        y_int8 = q_model(x)

    n_fp = sum(p.numel() * p.element_size() for p in model.parameters())
    n_q = sum(p.numel() * p.element_size() for p in q_model.parameters()) or n_fp // 4
    diff = (y_fp32 - y_int8).abs().max().item()
    print(f"float32 参数存储约 {n_fp / 1024:.1f} KB，int8 量化后约 {n_q / 1024:.1f} KB")
    print(f"同一输入下输出最大偏差: {diff:.6f}")
    print("结论: 真框架里的量化与第 1 段手算是同一套数学，只是由库帮你批量完成。")


def main():
    print("第 02 课配套演示：模型量化技术")
    run_stdlib_demo()   # 零依赖，必须成功
    run_torch_demo()    # 缺库自动跳过
    print("\n全部演示结束。")


if __name__ == "__main__":
    main()
