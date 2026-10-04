# -*- coding: utf-8 -*-
# 用途：输出解析器演示——离线主体用纯标准库走一遍"剥闲聊→解析→校验→带错重试"，
#       再列 PydanticOutputParser 的真实写法（装了 langchain 就能离线跑）。
# 安装：pip install langchain langchain-core pydantic python-dotenv
# 说明：情形1~4 与格式说明演示都不需要 API Key，可真跑；
#       联网链路（prompt | model | parser）需要 OPENAI_API_KEY，会产生少量费用，未实跑。

import json
import os

# 可选：从项目目录 .env 读环境变量（.env 不要提交到 git）
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# 期待模型按这张"表格"返回：字段名 -> 类型
EXPECTED = {"title": str, "rating": float, "pros": list}

FIXED_TEXT = (
    '{"title": "流浪地球2", "rating": 8.5, '
    '"pros": ["特效震撼", "多线叙事有格局"]}'
)


def parse_review(text: str) -> dict:
    """解析模型返回的文本：先剥闲聊找到 JSON，再逐字段校验，不合法抛中文错误。"""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("解析失败：返回内容里没找到 JSON 对象（连 { } 都没有）")

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        # 把出错位置一起报出来：模型看着报错才改得准，人也少翻一遍
        pos = start + exc.pos
        line = text[:pos].count("\n") + 1
        col = pos - text[:pos].rfind("\n")
        raise ValueError(f"JSON 语法错误（约第 {line} 行第 {col} 列）：{exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"解析失败：期望 JSON 对象，实际得到 {type(data).__name__}")

    for name, typ in EXPECTED.items():
        if name not in data:
            raise ValueError(f"字段缺失：{name}（期望 {typ.__name__}）")
        if typ is float and isinstance(data[name], (int, float)) and not isinstance(data[name], bool):
            continue  # JSON 里的 8 可以当 8.0 用；bool 是 int 的子类，要排除
        if not isinstance(data[name], typ):
            hint = "（评分给成文字了，应给 0-10 的数字）" if name == "rating" else ""
            raise ValueError(
                f"类型不对：{name} 期望 {typ.__name__}，"
                f"实际是 {type(data[name]).__name__}{hint}"
            )
    return data


def retry_once(text: str) -> dict:
    """带错重试一次：解析失败就把"原始回答+错误信息"退回去改，再重新解析。"""
    try:
        return parse_review(text)
    except ValueError as exc:
        print(f"\n第一次解析失败：{exc}")
        print("-> 把原始回答和错误信息发回模型请求修正（演示用写死的第二版回答模拟）")
        # 真实场景这里是一次模型调用，写法见下方 online_demo 里的 OutputFixingParser
        return parse_review(FIXED_TEXT)


def offline_main() -> None:
    """情形1~4 全程离线：只靠标准库，不需要 API Key。"""
    good = '''好的，这是简评：

```json
{"title": "流浪地球2", "rating": 8.5, "pros": ["特效震撼", "多线叙事有格局"]}
```

希望对你有帮助！
'''
    bad_syntax = '''好的，这是简评：

```json
{"title": "流浪地球2", "rating": 8.5, "pros": ["特效震撼", "多线叙事有格局"],}
```

希望对你有帮助！
'''
    bad_type = '{"title": "流浪地球2", "rating": "很高", "pros": ["特效震撼"]}'

    print("== 情形1：正常返回——剥闲聊、解析、校验 ==")
    review = parse_review(good)
    print("解析成功：")
    print("  title :", review["title"])
    print("  rating:", review["rating"], "是", type(review["rating"]).__name__)
    print("  pros  :", review["pros"])

    print("\n== 情形2：JSON 语法坏了（结尾多个逗号）——报清出错位置 ==")
    try:
        parse_review(bad_syntax)
    except ValueError as exc:
        print("解析失败：", exc)

    print("\n== 情形3：JSON 合法但字段类型不对——报清哪个字段 ==")
    try:
        parse_review(bad_type)
    except ValueError as exc:
        print("解析失败：", exc)

    print("\n== 情形4：带错重试一次（自动修复的套路）==")
    review2 = retry_once(bad_type)
    print("修复后解析成功：")
    print("  title :", review2["title"])
    print("  rating:", review2["rating"], "是", type(review2["rating"]).__name__)
    print("  pros  :", review2["pros"])


def _import_pydantic_parser():
    """PydanticOutputParser 在包之间挪过几次位置，两条导入路径都试一下。"""
    try:
        from langchain.output_parsers import PydanticOutputParser
    except ImportError:
        from langchain_core.output_parsers import PydanticOutputParser
    return PydanticOutputParser


def pydantic_demo() -> None:
    """PydanticOutputParser：生成格式说明、解析写死文本，都不需要 API Key。"""
    try:
        from pydantic import BaseModel, Field

        PydanticOutputParser = _import_pydantic_parser()
    except ImportError:
        print("\n== PydanticOutputParser 演示跳过：还没装 langchain/pydantic ==")
        print("   先执行：pip install langchain pydantic，再重跑本文件")
        return

    class MovieReview(BaseModel):
        """和讲义里同一个模型：字段、类型、含义。"""

        title: str = Field(description="电影名")
        rating: float = Field(description="0 到 10 的评分")
        pros: list[str] = Field(description="优点，2 到 3 条")

    parser = PydanticOutputParser(pydantic_object=MovieReview)

    print("\n== PydanticOutputParser 自动生成的格式说明（前几行）==")
    print("\n".join(parser.get_format_instructions().splitlines()[:6]))

    print("\n== 直接解析写死的模型回答（不需要 Key）==")
    review = parser.parse(FIXED_TEXT)
    print("解析成功：")
    print("  title :", review.title)
    print("  rating:", review.rating, "是", type(review.rating).__name__)
    print("  pros  :", review.pros)


def online_demo() -> None:
    """完整链 prompt | model | parser。需要 OPENAI_API_KEY，会产生少量费用。未实跑。"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from pydantic import BaseModel, Field

    PydanticOutputParser = _import_pydantic_parser()

    class MovieReview(BaseModel):
        title: str = Field(description="电影名")
        rating: float = Field(description="0 到 10 的评分")
        pros: list[str] = Field(description="优点，2 到 3 条")

    parser = PydanticOutputParser(pydantic_object=MovieReview)
    model = ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))  # 示例名可能已更新

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是影评助手，简短直接。\n{format_instructions}"),
            ("human", "给电影《{movie}》写个简评"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    review = (prompt | model | parser).invoke({"movie": "流浪地球2"})
    print("评分：", review.rating, "（是", type(review.rating).__name__, "，可直接入库）")

    # 解析失败时的自动修复：把原解析器包一层，失败就带着报错找模型改一次
    # from langchain.output_parsers import OutputFixingParser
    # fix_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
    # review = fix_parser.invoke(某段解析失败的原始回答)


def main() -> None:
    offline_main()
    pydantic_demo()

    if not os.environ.get("OPENAI_API_KEY"):
        print("\n提示：没设置 OPENAI_API_KEY，联网链路演示已跳过（该段未实跑）。")
        print("Windows：setx OPENAI_API_KEY 你的key（重开终端生效）")
        print("macOS/Linux：在 ~/.zshrc 或 ~/.bashrc 里加 export OPENAI_API_KEY=你的key")
        return

    print("\n== 联网链路（需要 API Key）==")
    try:
        online_demo()
    except Exception:
        print("联网调用失败。常见原因：Key 不对、网络不通、额度用完，逐项检查后重试。")


if __name__ == "__main__":
    main()
