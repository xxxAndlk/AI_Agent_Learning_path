class PythonGoComparator:
    """Python vs Go 对比工具"""
    
    def __init__(self):
        self.differences = {
            "类型系统": "动态 vs 静态",
            "编译方式": "解释 vs 编译",
            "并发模型": "asyncio vs Goroutine",
            "错误处理": "异常 vs 返回值",
            "性能": "灵活 vs 高效",
            "语法": "简洁 vs 明确"
        }
    
    def get_difference(self, aspect: str) -> str:
        """获取特定方面的差异"""
        return self.differences.get(aspect, "未知")
    
    def print_all(self):
        """打印所有差异"""
        print("="*50)
        print("Python vs Go 关键差异")
        print("="*50)
        for aspect, diff in self.differences.items():
            print(f"{aspect:12}: {diff}")


if __name__ == "__main__":
    # 运行对比
    comparator = PythonGoComparator()
    comparator.print_all()
