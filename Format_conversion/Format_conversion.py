import os
from PIL import Image
from tqdm import tqdm  # 进度条库

# 获取当前脚本的目录
当前目录 = os.path.dirname(os.path.abspath(__file__))

# 设置源文件夹和目标文件夹的绝对路径
源文件夹 = os.path.join(当前目录, 'input')
目标文件夹 = os.path.join(当前目录, 'output')

# 打印绝对路径，调试用
# print("源文件夹绝对路径:", 源文件夹)
# print("目标文件夹绝对路径:", 目标文件夹)

# 确保源文件夹存在（如果不存在则创建）
if not os.path.exists(源文件夹):
    os.makedirs(源文件夹)
    print(f"源文件夹 {源文件夹} 已创建，请将需要处理的文件放入该文件夹后重新运行脚本。")
    exit()  # 退出脚本，等待用户将文件放入

# 确保目标文件夹存在
if not os.path.exists(目标文件夹):
    os.makedirs(目标文件夹)

# 支持的图像格式
支持的格式 = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']

# 获取所有符合条件的文件
文件列表 = [文件名 for 文件名 in os.listdir(源文件夹) if os.path.splitext(文件名)[1].lower() in 支持的格式]

# 初始化计数器
计数器 = 0

# 遍历源文件夹中的所有文件并显示进度条
for 文件名 in tqdm(文件列表, desc="处理进度"):
    文件扩展名 = os.path.splitext(文件名)[1].lower()
    
    # 构建完整的文件路径
    源文件路径 = os.path.join(源文件夹, 文件名)
    目标文件路径 = os.path.join(目标文件夹, os.path.splitext(文件名)[0] + '.png')  # 使用原文件名，改为PNG扩展名

    try:
        # 打开图片
        with Image.open(源文件路径) as 图片:
            # 转换并保存为PNG格式
            图片.save(目标文件路径, 'PNG')
    except Exception as e:
        print(f'处理 {文件名} 时出错: {str(e)}')

print('WELL DONE!!❤')
