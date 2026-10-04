# -*- coding: utf-8 -*-
"""第05课配套：向量数据库选型 —— 纯标准库"提问-打分"决策器，跑三个真实场景。
全程零依赖。五问=五个输入项，硬约束一票否决，软偏好加减分，最后按分排序给推荐。"""

# 候选库画像：kind 形态 / scale_cap 规模舒适区上限 / filter 是否自带元数据过滤
# ops_need 需要的运维等级(0无/1少量/2专业) / cost 0免费自托管 1托管付费 / needs_server 是否要装服务
CANDS = {
    "FAISS":       dict(kind="嵌入式", scale_cap=10**8, filter=False, ops_need=0, cost=0, needs_server=False),
    "Chroma":      dict(kind="嵌入式", scale_cap=10**7, filter=True,  ops_need=0, cost=0, needs_server=False),
    "pgvector":    dict(kind="扩展插件", scale_cap=10**7, filter=True, ops_need=1, cost=0, needs_server=True),
    "Milvus Lite": dict(kind="嵌入式", scale_cap=10**6, filter=True,  ops_need=0, cost=0, needs_server=False),
    "Milvus 集群": dict(kind="分布式", scale_cap=10**10, filter=True, ops_need=2, cost=0, needs_server=True),
    "云托管":      dict(kind="托管服务", scale_cap=10**10, filter=True, ops_need=0, cost=1, needs_server=False),
}


def decide(scn):
    """五问 -> 打分。返回 [(分数, 名字, [理由], [警告])] 按分排序"""
    out = []
    for name, c in CANDS.items():
        score, why, warn = 50.0, [], []
        if scn["scale"] > c["scale_cap"]:                      # 问题1：规模
            score -= 40
            warn.append(f"规模 {scn['scale']:,} 超出舒适区 {c['scale_cap']:,}")
        else:
            why.append(f"规模 {scn['scale']:,} 在舒适区内")
        if scn["ops"] < c["ops_need"]:                         # 问题2：运维
            score -= 45
            warn.append(f"需要运维等级 {c['ops_need']}，团队只有 {scn['ops']}")
        if c["needs_server"] and scn["ops"] == 0:
            score -= 15
            why.append("要安装/部署服务，无人运维是负担")
        if name == "pgvector":                                 # 问题3：家底
            if scn["has_pg"]:
                score += 30
                why.append("复用已有 PostgreSQL，数据不搬家")
            else:
                score -= 25
                why.append("团队没有 PG，得先装一套数据库")
        if scn["need_filter"] and not c["filter"]:             # 问题4：功能
            score -= 40
            warn.append("无内置元数据过滤，要自己造轮子")
        if scn["budget"] == 0 and c["cost"] == 1:              # 问题5：预算
            score -= 35
            warn.append("托管按量付费，与'免费优先'冲突")
        if scn["budget"] == 1 and c["cost"] == 1 and scn["ops"] == 0 and scn["scale"] > 10**7:
            score += 25
            why.append("大规模+无人运维，托管省心正对口")
        if name == "Milvus 集群" and scn["scale"] < 10**7:
            score -= 35
            warn.append("数据不大，集群是杀鸡用牛刀")
        out.append((score, name, why, warn))
    return sorted(out, reverse=True)


def show(title, scn):
    print("\n" + "=" * 52)
    print(f"场景：{title}")
    print(f"  五问输入: 规模={scn['scale']:,} | 运维={scn['ops']}(0无/1少量/2专业) | "
          f"已有PG={scn['has_pg']} | 要过滤={scn['need_filter']} | 免费优先={scn['budget'] == 0}")
    print("=" * 52)
    for rank, (score, name, why, warn) in enumerate(decide(scn), 1):
        tag = " <-- 推荐" if rank == 1 else ""
        print(f"{rank}. {name}  得分 {score:.0f}{tag}")
        for w in why:
            print(f"     + {w}")
        for w in warn:
            print(f"     ! {w}")


def main():
    print("[纯标准库] 向量数据库选型决策器：五问打分 -> 排名推荐")
    show("个人 RAG 玩具", dict(scale=5 * 10**4, ops=0, has_pg=False,
                              need_filter=True, budget=0))
    show("已有 PostgreSQL 的中型知识库", dict(scale=5 * 10**5, ops=2, has_pg=True,
                                             need_filter=True, budget=0))
    show("亿级推荐系统", dict(scale=5 * 10**8, ops=2, has_pg=False,
                              need_filter=True, budget=1))
    print("\n想一想④ 自测：复制一份 show()，改成 '初创团队/50万条/无人运维'，看决策器选谁、为什么。")


if __name__ == "__main__":
    main()
