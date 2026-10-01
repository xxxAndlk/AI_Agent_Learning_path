# 快速验证想法
import random
from collections import Counter

def simulate_dice_rolls(num_rolls=10000):
    """模拟掷骰子"""
    results = [random.randint(1, 6) + random.randint(1, 6) 
               for _ in range(num_rolls)]
    
    distribution = Counter(results)
    for total in sorted(distribution.keys()):
        count = distribution[total]
        percentage = count / num_rolls * 100
        bar = '█' * int(percentage)
        print(f"{total:2d}: {bar} {percentage:.1f}%")

simulate_dice_rolls()
