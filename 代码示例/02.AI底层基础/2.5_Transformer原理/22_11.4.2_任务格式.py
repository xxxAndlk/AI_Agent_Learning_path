# T5的任务格式化
task_templates = {
    "cola": "cola sentence: {sentences}",  # 语言可接受性
    "sst2": "sst2 sentence: {sentences}",  # 情感分类
    "translation_en_de": "translate English to German: {english_text}",
    "summarization": "summarize: {document}",
    "question_answering": "question: {question} context: {context}"
}
