from functools import reduce

# 定义增强操作
def rotate(img, angle):
    return f"旋转{angle}度"

def flip(img, direction):
    return f"{direction}翻转"

def normalize(img):
    return f"归一化"

# 组合增强操作
def compose_augmentations(*operations):
    def augment(img):
        return reduce(lambda i, op: op(i), operations, img)
    return augment

# 创建增强管道
augment = compose_augmentations(
    lambda x: rotate(x, 15),
    lambda x: flip(x, "水平"),
    normalize
)
