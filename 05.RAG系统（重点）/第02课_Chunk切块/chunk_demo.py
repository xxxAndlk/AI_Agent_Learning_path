# chunk_demo.py —— 亲手体验"文档切块"：固定大小切块、重叠、简化版递归切块
# 纯标准库，无需 pip install 任何第三方库，直接运行：python chunk_demo.py

# 演示参数：块大小 50 字、相邻块重叠 20 字。改这两个数字再跑，观察句子被切断/接回的变化。
# 重叠 20 字（约块大小的 40%）是为了让"接住断句"的效果一眼可见，实际工程常从 10%～20% 起步。
CHUNK_SIZE = 50
OVERLAP = 20

# 演示文本：5 句话的"报销制度"，共 121 字，长度足够跨过切块边界
SENTENCES = [
    "公司报销制度：员工出差需保留发票，并在返程后三个工作日内提交。",
    "住宿费按城市分档，一线城市每晚不超过六百元。",
    "餐费实行包干制，每天一百元，不用提供发票。",
    "打车费以实际发生为准，单程超过两百元需提前报备。",
    "所有报销由直属主管审批，财务在每周五统一打款。",
]
TEXT = "".join(SENTENCES)

# 递归切块的分隔符优先级：先按段落（空行）、再按换行、再按句子、逗号逐级降级。
# 注意这是中文文档的写法——靠中文标点找边界；英文教程常见"按空格切词"的列表，对中文不适用。
# 列表走完还没切小，split() 里会按字符硬切兜底。
SEPARATORS = ["\n\n", "\n", "。", "，"]


def fixed_chunk(text, chunk_size, overlap=0):
    """固定大小切块：每 chunk_size 个字符切一刀，相邻块保留 overlap 个字符的重叠。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须是正整数")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap 必须满足 0 <= overlap < chunk_size，否则切块会原地打转")

    chunks = []
    start = 0
    while start < len(text):
        # 新窗口必须带来重叠区之外的新内容；否则剩下的全是上一块尾巴的重复，直接停
        if start > 0 and start + overlap >= len(text):
            break
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks


def recursive_chunk(text, chunk_size):
    """简化版递归切块：优先按段落、句子这些自然边界切，最后才硬切，再把小块贪心拼回去。

    演示重点是"沿边界切"，所以省去了重叠——它本来就少切断句子，重叠是给固定切块补的课。
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须是正整数")

    def split(txt, seps):
        if not seps:  # 分隔符全部用完：只能硬切
            return [txt[i:i + chunk_size] for i in range(0, len(txt), chunk_size)]
        sep, rest = seps[0], seps[1:]
        parts = txt.split(sep)
        # 把分隔符接回各片段尾部，保住标点和换行，切完读起来仍是通顺的
        parts = [p + sep for p in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
        pieces = []
        for p in parts:
            if not p:
                continue
            if len(p) > chunk_size:  # 这个片段自己还超长，降一级分隔符继续切它
                pieces.extend(split(p, rest))
            else:
                pieces.append(p)
        return pieces

    # 贪心合并：相邻片段尽量拼到接近 chunk_size，但绝不把任何片段再切开
    chunks, cur = [], ""
    for p in split(text, SEPARATORS):
        if cur and len(cur) + len(p) > chunk_size:
            chunks.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        chunks.append(cur)
    return chunks


def intact_sentences(chunks):
    """数一数：5 句话里有多少句"完整地"出现在某一个块里——被拦腰切断的不算。"""
    return sum(1 for s in SENTENCES if any(s in c for c in chunks))


def show(title, chunks):
    print("=" * 52)
    print(title)
    for i, c in enumerate(chunks, 1):
        print(f"块 {i}（{len(c)} 字）：{c}")
    print(f"→ 5 句话里 {intact_sentences(chunks)} 句保持完整")


def main():
    print(f"原文 {len(TEXT)} 字，由 {len(SENTENCES)} 句话组成：\n{TEXT}\n")

    show(f"① 固定大小切块：每 {CHUNK_SIZE} 字切一刀，不重叠",
         fixed_chunk(TEXT, CHUNK_SIZE))
    print("  （被切断的句子前后半截分了家，哪一块都读不全）\n")

    show(f"② 固定大小切块 + 重叠：块大小 {CHUNK_SIZE}、重叠 {OVERLAP}",
         fixed_chunk(TEXT, CHUNK_SIZE, overlap=OVERLAP))
    print("  （重叠区把断句'接'了回来：断口处的句子至少完整地落在一块里）\n")

    show(f"③ 递归切块：先按句子切，再拼回 {CHUNK_SIZE} 字以内",
         recursive_chunk(TEXT, CHUNK_SIZE))
    print("  （每块都从句子边界开始：递归切块从根上减少切断，工程里最常用）\n")

    print("结论：重叠是'事后补救'，递归是'从根上少切'，真实系统里两者经常一起用。")


if __name__ == "__main__":
    main()
