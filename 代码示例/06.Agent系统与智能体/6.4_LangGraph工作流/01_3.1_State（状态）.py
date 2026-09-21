from typing import TypedDict, Annotated, Sequence
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[dict], operator.add]  # 消息历史，使用Annotated实现增量更新
    next_step: str                                      # 下一步操作指示
    query: str                                          # 用户查询
    result: str                                         # 最终结果
    error: Optional[str]                                # 错误信息
