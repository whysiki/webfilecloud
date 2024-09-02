import re

# 示例文本，包含以 .ts 结尾的行
text = """
file1.ts
file2.mp4
file3.ts
file4.mov
"""

# 定义正则表达式模式
pattern = r".*\.ts$"

# 使用 re.findall() 查找所有匹配的行
matches = re.findall(pattern, text, flags=re.MULTILINE)

# 输出匹配结果
for match in matches:
    print(match)
