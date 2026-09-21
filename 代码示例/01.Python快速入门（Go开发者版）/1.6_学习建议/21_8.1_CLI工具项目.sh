# 搜索当前目录下所有.py文件
python search.py . -n "*.py"

# 搜索大于1MB的文件
python search.py . --min-size 1048576

# 搜索最近7天修改的文件
python search.py . --days 7
