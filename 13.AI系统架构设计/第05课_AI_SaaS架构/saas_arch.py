# saas_arch.py —— AI SaaS 架构骨架（第13章第05课配套）
# 用途：纯标准库模拟「入口网关 → 应用 → 模型网关 → 计量计费」+ 租户隔离与配额
# 运行：python saas_arch.py   零依赖零Key，直接真跑

# ============ 数据层：共享表 + tenant_id 字段隔离 ============
TENANTS = {
    "A公司": {"plan": "pro", "quota": 5000,  "used": 0},
    "B公司": {"plan": "free", "quota": 500,   "used": 0},
    "C公司": {"plan": "pro", "quota": 5000,  "used": 0},
}
SHARED_DOCS = [  # 共享向量库的模拟：靠 tenant_id 字段隔离，不靠分库
    {"tenant_id": "A公司", "text": "A公司的产品手册：支持批量导入"},
    {"tenant_id": "B公司", "text": "B公司的内部Wiki：报销用OA"},
]


# ============ 模型网关：主备两路供应商 ============
class ModelGateway:
    def __init__(self):
        self.providers = [{"name": "primary-A", "fail": False},
                          {"name": "backup-B", "fail": False}]
        self.meter = []  # 计量留痕：每次调用一条

    def call(self, tenant, prompt):
        for p in self.providers:
            if p["fail"]:
                continue
            # 真实系统：统一API + 按供应商适配提示词/参数
            cost = len(prompt) + 20
            self.meter.append({"tenant": tenant, "provider": p["name"], "tokens": cost})
            return f"回答（由 {p['name']} 生成）"
        return None  # 全挂：交给上层优雅降级


GATEWAY = ModelGateway()


# ============ 入口网关：认证 + 配额检查 + 限流 ============
def gateway_handle(tenant, prompt, per_min=3):
    t = TENANTS.get(tenant)
    if not t:
        return "401 未知租户"
    if t["used"] >= t["quota"]:
        return "429 配额已用完，请升级套餐或下月再来"   # 配额=商业化的刹车
    t["used"] += 1
    # 模型网关：主备切换
    ans = GATEWAY.call(tenant, prompt)
    if ans is None:
        return "503 所有模型供应商繁忙，请稍后重试（优雅降级）"
    # 检索租户自己的数据（字段隔离演示）
    mine = [d["text"] for d in SHARED_DOCS if d["tenant_id"] == tenant]
    return f"{ans}｜参考了 {len(mine)} 条本租户资料"


# ============ 计量计费：出账单 ============
def billing_report():
    print(f"{'租户':<6}{'调用量':>6}{'tokens':>8}{'配额':>8}  账单")
    for name, t in TENANTS.items():
        tokens = sum(m["tokens"] for m in GATEWAY.meter if m["tenant"] == name)
        unit = 0.02 if t["plan"] == "pro" else 0.05  # pro 走量便宜
        bill = tokens * unit
        print(f"{name:<6}{t['used']:>6}{tokens:>8}{t['quota']:>8}  ¥{bill:.2f}")


if __name__ == "__main__":
    print("=" * 60)
    print("演示 1：三个租户的正常调用（共享库按 tenant_id 隔离）")
    print("=" * 60)
    for tn in TENANTS:
        print(f"  {gateway_handle(tn, '帮我总结这个月的产品使用情况')}")
    print()
    print("=" * 60)
    print("演示 2：主供应商故障，模型网关自动切备用（高可用）")
    print("=" * 60)
    GATEWAY.providers[0]["fail"] = True
    print("  ", gateway_handle("A公司", "主路挂了试试备用路"))
    GATEWAY.providers[0]["fail"] = False
    print()
    print("=" * 60)
    print("演示 3：free 租户打爆配额，被网关拒之门外（配额视角）")
    print("=" * 60)
    for _ in range(499):
        gateway_handle("B公司", "继续调用")
    print("  ", gateway_handle("B公司", "最后一根稻草"))
    print()
    print("=" * 60)
    print("月底账单（计量计费：按 token 出账，pro 单价更低）")
    print("=" * 60)
    billing_report()
