# match-case有一定开销，适合多分支场景
# 简单条件仍用if-elif

# 推荐：少于3个分支用if-elif
if x == "a":
    return 1
elif x == "b":
    return 2

# 推荐：3个以上分支用match-case
match x:
    case "a": return 1
    case "b": return 2
    case "c": return 3
    case _: return 0
