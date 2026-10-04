class CustomTokenizer:
    """自定义特殊Token的Tokenizer"""
    
    def __init__(self, base_model="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        
        # 添加自定义特殊Token
        custom_special_tokens = {
            "[EOD]": "文档结束",
            "[URL]": "网址标记",
            "[EMAIL]": "邮箱标记",
            "[NUM]": "数字标记",
        }
        
        num_added = self.tokenizer.add_special_tokens({
            "additional_special_tokens": list(custom_special_tokens.keys())
        })
        
        print(f"添加了 {num_added} 个特殊Token")
        
        # 显示新token的ID
        for token, desc in custom_special_tokens.items():
            token_id = self.tokenizer.convert_tokens_to_ids(token)
            print(f"  {token} (ID: {token_id}): {desc}")
    
    def encode_with_special_tokens(self, text):
        """使用特殊Token编码"""
        return self.tokenizer.encode(text)
    
    def decode_with_special_tokens(self, token_ids):
        """解码，保留特殊Token"""
        return self.tokenizer.decode(token_ids)

def use_custom_special_tokens():
    """使用自定义特殊Token"""
    
    custom_tokenizer = CustomTokenizer()
    
    # 文本中包含需要标记的内容
    text = "欢迎访问[URL]www.example.com[URL]，如有疑问请联系[EOD]"
    
    # 编码
    encoded = custom_tokenizer.encode_with_special_tokens(text)
    tokens = custom_tokenizer.tokenizer.convert_ids_to_tokens(encoded)
    
    print(f"\n原文: {text}")
    print(f"分词: {tokens}")
    print(f"IDs: {encoded}")
    
    # 解码
    decoded = custom_tokenizer.decode_with_special_tokens(encoded)
    print(f"解码: {decoded}")

use_custom_special_tokens()
