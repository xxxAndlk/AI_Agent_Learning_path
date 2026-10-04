# -*- coding: utf-8 -*-
"""LLM 推理框架演示：模拟连续批处理调度 + KV Cache 显存块按需分配（PagedAttention 直觉）。

全程纯标准库，零依赖直接运行：python inference_framework_demo.py
vLLM 段需 pip install vllm（缺库打印中文提示并跳过）。
Ollama 本机实操见讲义【Ollama 本机实操锚点】：需本机安装，本脚本不代跑、未实跑。
"""
LINE = "-" * 52


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


# ---------- 第 1 段：静态批 vs 连续批处理 ----------

def run_batching_demo():
    banner("第 1 段：连续批处理调度（槽位池）")
    requests = [("A", 2), ("B", 5), ("C", 3), ("D", 4)]  # (请求, 还要生成的token数)
    slots = 4

    # 静态批：一起进，槽位锁死到最长完成
    remaining = [n for _, n in requests]
    rounds_static = max(remaining)
    wasted_static = sum(rounds_static - n for n in remaining)
    print(f"静态批: {slots} 个槽位全锁 {rounds_static} 轮，"
          f"空转槽位轮 {wasted_static} 个")

    # 连续批：完成即释放，队列补位
    queue = [list(r) for r in requests]
    active, done_log, rnd = [], [], 0
    while queue or active:
        rnd += 1
        while len(active) < slots and queue:
            active.append(queue.pop(0))
        still = []
        for name, need in active:
            need -= 1
            if need == 0:
                done_log.append(f"{name}@轮{rnd}")
            else:
                still.append([name, need])
        active = still
    print(f"连续批: 共 {rnd} 轮，完成记录 {done_log}")
    # 连续批的槽位轮 = 各请求轮数之和（无空转）
    eff = sum(n for _, n in requests)
    print(f"槽位轮消耗: 静态 {slots * rounds_static} vs 连续 {eff}"
          f"（省 {slots * rounds_static - eff}，越参差越省）")


# ---------- 第 2 段：显存块按需分配 ----------

def run_paging_demo():
    banner("第 2 段：KV Cache 分页按需分配（PagedAttention 直觉）")
    block_tokens = 4          # 每块存 4 个 token 的 KV
    max_len = 64              # 按最长可能预留的口径
    requests = [("A", 7), ("B", 3), ("C", 12), ("D", 5)]

    reserve = len(requests) * (max_len // block_tokens)
    print(f"传统预留: 每请求按最大 {max_len} token 预留 → "
          f"{len(requests)} x {max_len // block_tokens} = {reserve} 块")

    need_total = 0
    detail = []
    for name, n in requests:
        blocks = -(-n // block_tokens)   # 向上取整
        need_total += blocks
        detail.append(f"{name}:{n}tk→{blocks}块")
    print(f"分页按需: {' | '.join(detail)}")
    print(f"合计 {need_total} 块，比预留省 {reserve - need_total} 块"
          f"（{100 - need_total * 100 // reserve}% 显存接更多请求）")
    print("要点: 写满一页再领下一页，完成即整页归还——碎片消失，并发上限上移。")


# ---------- 第 3 段：vLLM 真实框架段（缺库跳过） ----------

def run_vllm_demo():
    banner("第 3 段：vLLM（需 pip install vllm）")
    try:
        import vllm  # noqa: F401
    except ImportError:
        print("[跳过] 本段需要 vLLM，请先执行: pip install vllm")
        print("       （安装体积大且需较新硬件，本课纯标准库段已覆盖核心直觉）")
        return
    # 已安装也只做展示，不在本课启动引擎（需下载模型权重，讲义演示不越界）
    print(f"检测到 vLLM {getattr(vllm, '__version__', '未知版本')} 已安装。")
    print("真实用法（示意，不在本课运行）：")
    print('  from vllm import LLM, SamplingParams')
    print('  llm = LLM(model="开源模型名")   # 模型名按官网当前列表替换')
    print('  outs = llm.generate(["你好"], SamplingParams(max_tokens=64))')


# ---------- 第 4 段：Ollama 本机实操（命令指引，不代跑） ----------

def run_ollama_guide():
    banner("第 4 段：Ollama 本机实操锚点（需本机安装，未实跑）")
    print("本段只给命令指引，脚本不代跑；装好即可在本机聊开源模型：")
    print("  1) 官网 https://ollama.com 下载安装（Linux: curl -fsSL https://ollama.com/install.sh | sh）")
    print("  2) ollama pull qwen3      # 示例名，按官网模型库当前列表替换")
    print("  3) ollama run qwen3       # 进入对话，/bye 退出")
    print("  4) ollama list            # 查看本地模型")
    print("提示: 首次 pull 下载数 GB；模型大小量力选择，本机内存/显存是硬边界。")


def main():
    print("第 04 课配套演示：LLM 推理框架（纯标准库段零依赖）")
    run_batching_demo()     # 零依赖，必须成功
    run_paging_demo()       # 零依赖，必须成功
    run_vllm_demo()         # 缺库自动跳过
    run_ollama_guide()      # 命令指引，不实跑
    print("\n全部演示结束。")


if __name__ == "__main__":
    main()
