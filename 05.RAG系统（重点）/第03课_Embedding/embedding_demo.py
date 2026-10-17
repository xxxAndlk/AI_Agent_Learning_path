# embedding_demo.py —— 第03课配套演示：手工小向量算余弦相似度，体会"语义坐标"检索
# 主体离线实跑：纯标准库，无需安装任何包，直接 python embedding_demo.py
# 结尾的"真实嵌入 API"段：DeepSeek 不提供 embedding 接口，本课一律用本地手工向量演示；
# 生产可选 BGE / 通义千问 / 智谱等嵌入服务（调用形状见 demo_real_api 内注释，需各自 API Key，未实跑）

import math
import sys

# Windows 控制台默认 GBK，中文容易乱码：强制按 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 我们假扮一个"嵌入模型"：每个句子的向量是手工拍的。
# 四个维度含义：[动物, 休息, 食物, 天气]。
# 真实模型的维度成百上千，且由训练学出，不是人拍——这里为了看得见摸得着，故意拍小。
DOCUMENTS = [
    ("小猫在沙发上睡觉",     [0.9, 0.8, 0.00, 0.10]),
    ("小狗趴在垫子上打盹",   [0.9, 0.9, 0.00, 0.00]),
    ("今晚吃火锅还是烤肉",   [0.0, 0.1, 0.95, 0.00]),
    ("明天下雨出门记得带伞", [0.0, 0.0, 0.05, 0.95]),
    ("猫咪蜷在窝里呼呼大睡", [0.8, 0.9, 0.00, 0.00]),
]


def cosine(a, b):
    """余弦相似度：先算点积，再除以两个向量的长度，只比方向、不比长短。"""
    dot = sum(x * y for x, y in zip(a, b))
    len_a = math.sqrt(sum(x * x for x in a))
    len_b = math.sqrt(sum(x * x for x in b))
    if len_a == 0 or len_b == 0:
        return 0.0
    return dot / (len_a * len_b)


def normalize(v):
    """把向量缩放成长度为 1 的标准长度，之后点积就直接等于余弦相似度。"""
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else v


def demo_pair_scores():
    """相似句对分数高、不相关句对分数低——检索能工作的根基。"""
    print("=" * 50)
    print("第一部分：句对的余弦相似度（越接近 1 越像）")
    print("=" * 50)
    # 前三组意思相近，后三组风马牛不相及
    pairs = [(0, 4), (0, 1), (1, 4), (0, 2), (2, 3), (1, 3)]
    for i, j in pairs:
        score = cosine(DOCUMENTS[i][1], DOCUMENTS[j][1])
        tag = "相似" if score > 0.9 else "不相关"
        print(f"  [{tag}] {DOCUMENTS[i][0]}  vs  {DOCUMENTS[j][0]}  ->  {score:+.3f}")


def demo_query_topk(k=3):
    """检索的雏形：把问题变成向量，按余弦相似度取最相关的 top-k 条。"""
    # 问题向量带一点无关成分，更接近真实检索：相关句仍在 0.99 以上，不相关句跌到 0.1 附近
    query_text, query_vec = "宠物在打瞌睡", [0.85, 0.85, 0.05, 0.10]
    print()
    print("=" * 50)
    print(f"第二部分：检索——问题「{query_text}」取 top-{k}")
    print("=" * 50)
    ranked = sorted(DOCUMENTS, key=lambda d: cosine(query_vec, d[1]), reverse=True)
    for rank, (text, vec) in enumerate(ranked[:k], start=1):
        print(f"  第{rank}名  余弦={cosine(query_vec, vec):.3f}  {text}")


def demo_normalization():
    """归一化之后，点积 == 余弦相似度——很多向量库靠这个提速。"""
    a, b = DOCUMENTS[0][1], DOCUMENTS[4][1]
    via_cos = cosine(a, b)
    via_dot = sum(x * y for x, y in zip(normalize(a), normalize(b)))
    print()
    print("=" * 50)
    print("第三部分：归一化后，点积就是余弦")
    print("=" * 50)
    print(f"  余弦相似度   = {via_cos:.6f}")
    print(f"  归一化后点积 = {via_dot:.6f}   （两个值相等）")


def demo_real_api():
    """讲解真实嵌入 API 的接法。DeepSeek 不提供 embedding 接口，本函数只讲解不联网，
    不伪造任何嵌入调用；主体演示全部由上面的本地手工向量完成（离线可跑）。"""
    print()
    print("=" * 50)
    print("第四部分：真实嵌入 API 怎么接（讲解段，不联网）")
    print("=" * 50)
    print("  说明：DeepSeek 不提供 embedding 接口，所以本课检索用本地手工向量演示。")
    print("  生产中需要语义检索时，可换用带嵌入服务的方案，例如：")
    print("    - BGE 系列：开源可本地部署（如 BGE-M3，多语言、对中文友好）")
    print("    - 通义千问 / 智谱：商业嵌入 API，按量付费")
    print("  调用形状大致如下（各家 SDK 略异，以官网文档为准；需各自 API Key，未实跑）：")
    # ---- 真实嵌入 API 的调用形状（教学参考注释，本课不执行，严禁伪造输出）----
    # from openai import OpenAI   # 兼容 openai SDK 的嵌入服务商（DeepSeek 无 embedding，不能用它做嵌入）
    # client = OpenAI(api_key="你的嵌入服务商Key", base_url="该服务商的 base_url")
    # resp = client.embeddings.create(model="该服务商的嵌入模型名", input=["小猫在沙发上睡觉"])
    # vec = resp.data[0].embedding  # 得到向量后，余弦相似度用法与本课手工向量完全相同


if __name__ == "__main__":
    demo_pair_scores()
    demo_query_topk()
    demo_normalization()
    demo_real_api()
