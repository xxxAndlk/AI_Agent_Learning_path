# -*- coding: utf-8 -*-
"""推理引擎优化演示：模拟算子融合、显存复用、批处理，对比优化前后的操作步数。

全程纯标准库，零依赖直接运行：python inference_engine_demo.py
"""
LINE = "-" * 52


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


# ---------- 第 1 段：算子融合 ----------

def run_fusion_demo():
    banner("第 1 段：算子融合 —— 三道小菜炒成一锅")
    print("计算链: y = 激活( 权重·x + 偏置 )")
    print("逐算子跑: 每步 读显存 -> 计算 -> 写显存")
    n_ops = 3          # 乘、加、激活
    n_rw = n_ops * 2   # 每算子一读一写
    print(f"  操作数 {n_ops}，显存往返 {n_rw} 次")
    print("融合后: 数据读出一次，三步在手上一气呵成")
    print(f"  操作数 1，显存往返 2 次")
    print(f"-> 显存往返从 {n_rw} 降到 2，省 {n_rw - 2} 次仓库跑腿（灵活度下降为代价）")
    # 数值演示：两条路结果一致
    w, x, b = 2.0, 3.0, 1.0
    stepwise = max(0.0, (w * x) + b) if (w * x) + b > 0 else 0.0
    fused = max(0.0, w * x + b)
    print(f"  数值校验: 逐算子 {stepwise} | 融合 {fused} | 一致: {stepwise == fused}")


# ---------- 第 2 段：显存复用 ----------

def run_memory_demo():
    banner("第 2 段：显存复用 —— 钟点房式接力")
    # 算子时间表：(名字, 开始轮, 结束轮, 占块数)；块=显存计量单位
    schedule = [("conv1", 0, 2, 4), ("relu1", 2, 3, 4), ("conv2", 3, 5, 6),
                ("pool", 5, 6, 2), ("fc", 6, 8, 3)]
    slots = []          # [(释放轮, 容量)]
    peak_no_reuse, peak_reuse = 0, 0
    cur = 0
    for _, s, e, need in schedule:
        peak_no_reuse += need
        # 找一块在 start 轮前已释放、容量够的旧块
        for i, (free_at, cap) in enumerate(slots):
            if free_at <= s and cap >= need:
                slots[i] = (e, cap)
                break
        else:
            slots.append((e, need))
            cur += need
        peak_reuse = max(peak_reuse, cur)
    print("算子占用时间表:", [(n, f"{s}-{e}", f"{c}块") for n, s, e, c in schedule])
    print(f"不复用: 累计申请 {peak_no_reuse} 块")
    print(f"复用后: 峰值只需 {peak_reuse} 块（省 {peak_no_reuse - peak_reuse} 块）")
    print("要点: 引擎预先分析'谁先用完谁先退'，同一块地接力住客。")


# ---------- 第 3 段：批处理 ----------

def run_batch_demo():
    banner("第 3 段：批处理 —— 拼车出行")
    n_requests = 8   # 8 个请求排队
    print(f"场景: {n_requests} 个请求，每个都要过同一层网络")

    # 逐个处理：每请求一趟完整往返
    solo_steps = n_requests * 4   # 每请求: 读入/算/写/读出 4 步
    print(f"逐个处理: {n_requests} 趟 x 每趟 4 步 = {solo_steps} 操作步")

    # 拼批处理：一趟搬一批，搬运步骤摊薄
    for batch in (2, 4, 8):
        trips = -(-n_requests // batch)  # 向上取整趟数
        # 每趟: 读入(摊薄 1 步) + 矩阵乘按请求计 + 写出(摊薄 1 步)
        batched_steps = trips * (2 + batch)
        print(f"批 {batch}: {trips} 趟 x (搬运2 + 计算{batch}) = {batched_steps} 步"
              f" | 相对逐个省 {100 - batched_steps * 100 // solo_steps}%")

    print("\n交换关系: 批越大 -> 总步数越省(吞吐越高) | 但队头请求等待轮数越多(延迟↑)")
    # 最晚请求的等待轮数 = 最后一趟开始前的趟数
    for batch in (2, 4, 8):
        trips = -(-n_requests // batch)
        print(f"  批 {batch}: 最晚请求等 {trips - 1} 趟后才上车")
    print("-> 没有'最优批大小'，只有按业务偏好拧出来的旋钮。")


def main():
    print("第 03 课配套演示：推理引擎与优化（纯标准库，零依赖）")
    run_fusion_demo()
    run_memory_demo()
    run_batch_demo()
    print("\n全部演示结束。")


if __name__ == "__main__":
    main()
