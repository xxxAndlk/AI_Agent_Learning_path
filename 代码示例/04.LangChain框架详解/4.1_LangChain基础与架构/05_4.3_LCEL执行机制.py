# 定义链
chain = component_a | component_b | component_c

# 执行时内部流程：
# 1. component_a.invoke(input) → output_a
# 2. component_b.invoke(output_a) → output_b  
# 3. component_c.invoke(output_b) → final_output

# 流式执行：
# 每个组件的stream()方法被调用，输出通过生成器传递
