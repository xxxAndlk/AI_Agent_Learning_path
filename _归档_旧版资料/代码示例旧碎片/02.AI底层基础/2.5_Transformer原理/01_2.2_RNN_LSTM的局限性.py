# RNN的顺序处理（伪代码）
hidden = 0
for word in sentence:           # 必须顺序处理每个词
    hidden = rnn(word, hidden)  # 当前步依赖前一步
    # 问题：无法并行，长序列梯度消失
