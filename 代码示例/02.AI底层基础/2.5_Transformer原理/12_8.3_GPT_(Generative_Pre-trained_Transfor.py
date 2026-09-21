# GPT使用示例
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

input_text = "The quick brown fox"
input_ids = tokenizer.encode(input_text, return_tensors='pt')

# 生成文本
output = model.generate(
    input_ids, 
    max_length=50, 
    num_return_sequences=1,
    temperature=0.7
)

generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
