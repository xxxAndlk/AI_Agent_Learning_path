from datasets import Dataset
from transformers import DataCollatorForSeq2Seq

def prepare_dataset(examples, tokenizer, max_length=512):
    """准备指令微调数据"""
    
    # 构建输入文本
    texts = []
    for example in examples:
        text = f"### Instruction:\n{example['instruction']}\n\n"
        if example.get('input'):
            text += f"### Input:\n{example['input']}\n\n"
        text += f"### Response:\n{example['output']}"
        texts.append(text)
    
    # Tokenize
    model_inputs = tokenizer(
        texts,
        max_length=max_length,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )
    
    # 对于因果LM，标签就是输入本身
    model_inputs["labels"] = model_inputs["input_ids"].clone()
    
    return model_inputs

# 数据整理器
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True,
)
