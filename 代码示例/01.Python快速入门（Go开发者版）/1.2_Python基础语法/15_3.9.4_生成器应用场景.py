# ============ 大文件逐行读取（对比Go） ============
# Go:
# func readFileLineByLine(filename string) {
#     file, _ := os.Open(filename)
#     defer file.Close()
#     scanner := bufio.NewScanner(file)
#     for scanner.Scan() {
#         fmt.Println(scanner.Text())
#     }
# }

# Python: 使用生成器处理大文件
def read_large_file(file_path, chunk_size=1024):
    """
    大文件逐行读取 - 不会将整个文件加载到内存
    chunk_size: 每次读取的字节数
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break
            yield line.strip()  # 惰性返回，按需读取

# 使用示例：处理100GB日志文件
def analyze_log_file(file_path):
    """分析日志文件，统计错误数量"""
    error_count = 0
    for line in read_large_file(file_path):
        if "ERROR" in line:
            error_count += 1
    return error_count

# 分块读取（适合二进制文件）
def read_in_chunks(file_path, chunk_size=8192):
    """分块读取文件，适合处理大二进制文件"""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# 处理CSV大文件
import csv

def process_large_csv(file_path):
    """处理大型CSV文件 - 内存友好"""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row  # 每行处理完后才读取下一行

# 使用示例
def count_csv_rows(file_path):
    count = 0
    for _ in process_large_csv(file_path):
        count += 1
    return count
