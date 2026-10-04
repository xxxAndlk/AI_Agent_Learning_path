"""observability_demo.py —— 最小可观测性：给迷你 RAG 全程加 trace_id + 分步 span 日志（可跑版）。

运行：python observability_demo.py（trace 写入临时目录，跑完自动清理）
LangSmith 为可选段，缺库时中文提示跳过。
（对应第 11 章第 04 课；traces 日志即第 12 章第 04 课 Dashboard"链路详情"面板的数据源）
"""
import json
import tempfile
import time
import uuid
from pathlib import Path

DOCS = [
    "团建费用由公司承担，每人每季度上限 300 元。",
    "报销需要主管审批，通过后 5 个工作日到账。",
    "年假可在次年 3 月底前补休，过期作废。",
]


class Tracer:
    """一次调用的追踪器：入口发 trace_id，每步一个 span，finish 时打印树+存档。"""

    def __init__(self, name: str, out_path: Path):
        self.trace_id = uuid.uuid4().hex[:8]
        self.name = name
        self.out_path = out_path
        self.spans: list[dict] = []

    def start_span(self, step: str) -> dict:
        span = {"step": step, "start": time.perf_counter(), "attrs": {}}
        return span

    def end_span(self, span: dict, **attrs) -> None:
        span["dur_ms"] = round((time.perf_counter() - span["start"]) * 1000, 1)
        span["attrs"] = attrs
        self.spans.append({k: span[k] for k in ("step", "dur_ms", "attrs")})

    def finish(self, error: str | None = None) -> None:
        total = sum(s["dur_ms"] for s in self.spans)
        print(f"\ntrace_id={self.trace_id}（{self.name}）总耗时 {total:.0f}ms")
        for s in self.spans:
            attrs = " ".join(f"{k}={v}" for k, v in s["attrs"].items())
            print(f"  ├─ {s['step']:<8} {s['dur_ms']:>7}ms  {attrs}")
        if error:
            print(f"  └─ [报错定位] {error}")
        self.out_path.write_text(json.dumps(
            {"trace_id": self.trace_id, "name": self.name,
             "spans": self.spans, "error": error}, ensure_ascii=False), encoding="utf-8")


def rag_call(query: str, docs: list[str], out_path: Path, answers: dict) -> None:
    """迷你 RAG：切块→检索→拼提示→生成，全程留痕。这就是"给 mini_rag 加调用日志"。"""
    tracer = Tracer(query, out_path)

    sp = tracer.start_span("切块")
    chunks = [d for d in docs]  # 演示里一段一条，真实项目这里做切分
    tracer.end_span(sp, n_chunks=len(chunks))

    sp = tracer.start_span("检索")
    q_words = set(query)
    scored = [(c, len(q_words & set(c)) / max(len(q_words), 1)) for c in chunks]
    scored.sort(key=lambda x: -x[1])
    hits = [c for c, s in scored if s > 0][:3]
    tracer.end_span(sp, hits=len(hits), top_score=round(scored[0][1], 2))

    sp = tracer.start_span("拼提示")
    prompt = "\n".join(hits) + f"\n问题：{query}" if hits else f"问题：{query}"
    tracer.end_span(sp, prompt_len=len(prompt))

    sp = tracer.start_span("生成")
    if not hits:  # 检索扑空还硬生成 = 答案胡说的根源，日志里必须看得见
        tracer.end_span(sp, tokens=12, note="无知识块可用")
        tracer.finish(error="检索命中 0 条，生成只能靠模型瞎编 -> 答案不可信")
        return
    answer = answers.get(query, "根据知识库：……")
    time.sleep(0.05)  # 模拟模型生成耗时
    tracer.end_span(sp, tokens=len(answer))
    tracer.finish()


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "traces.jsonl"
        print("== 两次调用：一次正常，一次检索扑空（看日志如何定位病灶）==")
        rag_call("团建费用谁出？报销要审批吗？", DOCS, out,
                 answers={"团建费用谁出？报销要审批吗？": "团建费用由公司承担；报销需主管审批，5 个工作日到账。"})
        rag_call("外星人什么时候入侵地球？", DOCS, out, answers={})
        print(f"\ntrace 已存档 -> {out.name}（每行一个 json：这就是生产里 trace 存储的最小形态）")

        try:
            import langsmith  # noqa: F401
            print("检测到 langsmith：真实平台把同样的 span 概念接入云端，网页上展开每一步。")
        except ImportError:
            print("（可选段）未安装 langsmith，跳过平台演示。想试：pip install langsmith")


if __name__ == "__main__":
    main()
