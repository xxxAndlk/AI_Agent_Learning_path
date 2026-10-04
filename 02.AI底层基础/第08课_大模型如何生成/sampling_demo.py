# -*- coding: utf-8 -*-
"""手写采样演示：同一组打分，低温度和高温度各抽 20 次。

模型对下一个词只产出分数（logits），除以温度、再归一成支持率；
温度低，强者愈强，几乎每次都抽到同一个词；
温度高，差距被抹平，冷门词也有翻身的机会。
纯标准库，运行方式：python sampling_demo.py
"""
import math
import random
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # 防 Windows GBK 控制台中文乱码

candidates = ["天气", "心情", "火锅", "哲学"]  # 假想词表里排前几名的候选词
logits = [3.0, 2.0, 1.0, 0.0]  # 人为设定的原始分数，第 1 名比第 2 名强一截

# 固定随机种子，每次运行结果一致、方便对照课文；删掉这行即可看到真正的随机性
random.seed(7)


def softmax(scores, temperature):
    # 先按温度压小/放大分数差距，再归一成百分比；减最大值只为防 exp 溢出，不改变比例
    scaled = [s / temperature for s in scores]
    peak = max(scaled)
    weights = [math.exp(v - peak) for v in scaled]
    total = sum(weights)
    return [w / total for w in weights]


def show(temperature, times=20):
    probs = softmax(logits, temperature)
    counter = dict.fromkeys(candidates, 0)
    for _ in range(times):
        word = random.choices(candidates, weights=probs)[0]
        counter[word] += 1
    rates = "  ".join(f"{w} {p:5.1%}" for w, p in zip(candidates, probs))
    hits = "  ".join(f"{w}:{n}次" for w, n in counter.items())
    print(f"温度={temperature}  支持率: {rates}")
    print(f"          抽{times}次: {hits}")


show(0.5)
print()
show(2.0)
