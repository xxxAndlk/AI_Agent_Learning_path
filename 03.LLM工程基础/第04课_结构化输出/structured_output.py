# structured_output.py —— 第04课演示：让模型按 JSON Schema 交"报销单"（结构化输出）
# pip install openai pydantic python-dotenv
# 运行：python structured_output.py
#   - parse_demo 离线部分：纯标准库即可跑（本机已实跑通过）
#   - API 演示部分：需环境变量 OPENAI_API_KEY（需 Key，未实跑）

import json
import os
from typing import Literal

try:  # 本地把 Key 放在 .env 里更安全（.env 不要提交到 git）；没装这个库也不影响
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:  # pydantic 负责校验；没装也能跑离线小练，只是少了最后一道把关
    from pydantic import BaseModel, Field, ValidationError
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

if HAS_PYDANTIC:

    class CommentAnalysis(BaseModel):
        """一张"评论分析报销单"：字段怎么定，取决于下游代码要怎么用。"""
        sentiment: Literal["positive", "neutral", "negative"]  # 三选一，程序才好写 if 判断
        rating: int = Field(ge=1, le=5)                        # 1~5 星，超出范围当场打回
        keywords: list[str] = Field(max_length=5)              # 最多 5 个，够下游做统计
        note: str | None = None                                # 备注可空（null），但格子在


# ---------- 1. 表的两种写法：JSON Schema 与 Pydantic 模型是等价的 ----------

COMMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5},
        "keywords": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "note": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": ["sentiment", "rating", "keywords", "note"],
    "additionalProperties": False,
}
# 上面这份 Schema 不必手写：装好 pydantic 后执行 CommentAnalysis.model_json_schema()
# 就能生成等价物（strict 模式要求可选字段也出现在 required 里，允许值为 null）。


# ---------- 2. 稳健解析：剥围栏 -> json.loads -> Pydantic 校验 ----------

def extract_json(text: str) -> str:
    """从模型返回里抠出 JSON：先剥 Markdown 代码围栏，再取最外层大括号之间的片段。"""
    text = text.strip()
    if "```" in text:  # Markdown 围栏：取一对 ``` 之间的内容
        first = text.find("```")
        second = text.find("```", first + 3)
        if second != -1:
            text = text[first + 3:second].strip()
            if "\n" in text:  # 去掉开头可能的语言标记，如 json
                text = text.split("\n", 1)[1].strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1:
        raise ValueError("返回内容里没有找到 JSON（模型可能没按要求返回）")
    if end == -1 or end < start:
        raise ValueError("JSON 似乎被截断了：有开头的 { 却没有配对的 }")
    return text[start:end + 1]


def robust_parse(text: str):
    """不盲目信任返回：解析失败给中文报错；装了 pydantic 再加一道字段校验。"""
    try:
        payload = json.loads(extract_json(text))
    except json.JSONDecodeError as e:  # JSONDecodeError 原文是英文，翻译成人话
        raise ValueError(f"返回内容不是合法 JSON：{e.msg}（大约在第 {e.pos} 个字符）") from e
    if HAS_PYDANTIC:
        return CommentAnalysis.model_validate(payload)  # 类型不对/缺字段/超范围在这里暴露
    return payload


# ---------- 3. parse_demo：离线小练，没有 Key 也要能跑 ----------

GOOD_RETURN = (
    "好的，以下是这条评论的分析结果：\n"
    "```json\n"
    '{"sentiment": "negative", "rating": 2, "keywords": ["电池", "发热"], '
    '"note": "疑似质量问题"}\n'
    "```\n"
    "希望对你有帮助！"
)
BROKEN_RETURN = '分析结果：{"sentiment": "positive", "rating": 5,'   # 半截 JSON：返回被截断
WRONG_VALUES = '{"sentiment": "很差", "rating": 9, "keywords": []}'  # JSON 合法，但值不合规


def parse_demo():
    print("=" * 52)
    print("parse_demo（离线）：解析三段写死的\"模型返回\"")
    print("=" * 52)
    cases = [
        ("案例1 带代码围栏的正常返回", GOOD_RETURN),
        ("案例2 半截 JSON（返回被截断）", BROKEN_RETURN),
        ("案例3 JSON 合法但值不合规", WRONG_VALUES),
    ]
    for title, text in cases:
        print(f"\n{title}")
        print(f"  原文：{text[:44]}...")
        try:
            result = robust_parse(text)
        except Exception as e:
            print(f"  [失败] {e}")
            continue
        if HAS_PYDANTIC:
            print(f"  [成功] 情感={result.sentiment}  星级={result.rating}  "
                  f"关键词={result.keywords}  备注={result.note}")
        else:
            # 没有校验器时，案例3的坏值也会"解析成功"——这正是盲信返回的风险
            print(f"  [成功] {result}")
            print("  （注意：没装 pydantic，这种坏值也混过来了）")
    if not HAS_PYDANTIC:
        print("\n提示：pip install pydantic 后重跑，案例3会被字段校验当场打回。")


# ---------- 4. API 演示：Responses API + JSON Schema，需 Key 未实跑 ----------

MODEL_NAME = "gpt-4o-mini"  # 示例名，随时可能更新：按平台模型列表选个便宜够用的
PROMPT_TEMPLATE = "分析下面这条电商评论的情感、星级与关键词。评论：\n{comment}"


def build_client():
    """Key 只从环境变量读，绝不写进代码；SDK 默认读的就是 OPENAI_API_KEY。"""
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("缺少第三方库：请先执行 pip install openai pydantic python-dotenv")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("未检测到 OPENAI_API_KEY：请按第01课的方法设置环境变量（或写入 .env）后重试")
    return OpenAI()


def call_model(client, prompt: str) -> str:
    """格式约束交给接口层：text.format 指定 json_schema，模型想跑偏都难。"""
    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={"format": {
            "type": "json_schema",
            "name": "comment_analysis",
            "strict": True,
            "schema": COMMENT_SCHEMA,
        }},
    )
    return response.output_text


def analyze_comment(client, comment: str):
    """分析一条评论；解析/校验失败时，带着错误信息重试一次——圈出错题再让模型改。"""
    try:
        raw = call_model(client, PROMPT_TEMPLATE.format(comment=comment))
        return robust_parse(raw)
    except SystemExit:
        raise
    except Exception as e:
        first_error = str(e)  # 先存下来：except 块结束后变量 e 就被回收了
        print(f"  第一次返回未通过（{first_error}），带着错误信息重试一次...")
    fix_prompt = (f"你上次返回的内容没通过校验，错误信息：{first_error}\n"
                  "请严格按原要求重新返回，只返回 JSON，不要任何解释。")
    try:
        return robust_parse(call_model(client, fix_prompt))
    except Exception as e2:
        raise SystemExit(f"重试后仍未通过，先记日志、转人工检查：{e2}")


def main():
    parse_demo()  # 离线部分永远先跑，练手感不花钱

    print("\n" + "=" * 52)
    print("API 演示（需 OPENAI_API_KEY，未设置则跳过）")
    print("=" * 52)
    if not os.environ.get("OPENAI_API_KEY"):
        print("未检测到 OPENAI_API_KEY，跳过真实调用。设置好环境变量后重跑即可。")
        return
    if not HAS_PYDANTIC:
        print("未安装 pydantic（缺少最后一道校验），跳过 API 演示。")
        return
    comment = "用了一周就发热严重，电池也扛不住半天，联系客服半天没人理，失望。"
    try:
        result = analyze_comment(build_client(), comment)
    except SystemExit as e:
        print(e)  # 中文友好提示已在 analyze_comment 里备好，不抛裸 traceback
        return
    print(f"评论：{comment}")
    print(f"情感：{result.sentiment}   星级：{result.rating}")
    print(f"关键词：{result.keywords}   备注：{result.note}")


if __name__ == "__main__":
    main()
