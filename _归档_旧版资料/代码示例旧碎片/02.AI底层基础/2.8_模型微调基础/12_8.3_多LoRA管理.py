# 动态加载多个LoRA
from peft import PeftModel

class MultiLoRAManager:
    def __init__(self, base_model_path):
        self.base_model = AutoModelForCausalLM.from_pretrained(base_model_path)
        self.loras = {}
    
    def load_lora(self, name, lora_path):
        """加载LoRA适配器"""
        self.loras[name] = PeftModel.from_pretrained(
            self.base_model, lora_path
        )
    
    def switch_lora(self, name):
        """切换LoRA"""
        return self.loras.get(name, self.base_model)
    
    def merge_loras(self, names, weights):
        """合并多个LoRA"""
        # 加权合并多个LoRA的能力
        pass

# 使用示例
manager = MultiLoRAManager("Qwen/Qwen-7B")
manager.load_lora("medical", "./medical_lora")
manager.load_lora("legal", "./legal_lora")

# 根据用户问题切换
if is_medical_question(query):
    model = manager.switch_lora("medical")
else:
    model = manager.switch_lora("legal")
