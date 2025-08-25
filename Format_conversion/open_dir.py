import os
from PIL import Image
from tqdm import tqdm

def resize_image(image_path, output_path, target_size):
    with Image.open(image_path) as img:
        # 获取原始图像的宽度和高度
        width, height = img.size
        
        # 计算缩放比例
        aspect_ratio = width / height
        if width > height:
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
        else:
            new_height = target_size
            new_width = int(target_size * aspect_ratio)
        
        # 调整图像大小
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 保存调整后的图像
        resized_img.save(output_path)

def process_images(input_dir, output_dir, target_sizes):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有图像文件
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    # 使用tqdm创建进度条
    for image_file in tqdm(image_files, desc="处理图像"):
        input_path = os.path.join(input_dir, image_file)
        
        for target_size in target_sizes:
            output_subdir = os.path.join(output_dir, f"{target_size}")
            os.makedirs(output_subdir, exist_ok=True)
            
            output_path = os.path.join(output_subdir, image_file)
            resize_image(input_path, output_path, target_size)

# 使用示例
# 获取当前脚本的目录
当前目录 = os.path.dirname(os.path.abspath(__file__))

# 设置源文件夹和目标文件夹的绝对路径
input_directory = os.path.join(当前目录, 'input')
output_directory = os.path.join(当前目录, 'output')
target_sizes = []
while True:
    size = input("请输入目标尺寸（输入完成后按回车，输入'完成'结束）: ")
    if size.lower() == '完成':
        break
    try:
        target_sizes.append(int(size))
    except ValueError:
        print("请输入有效的整数尺寸。")
if not target_sizes:
    print("未输入任何尺寸，将使用默认尺寸：512, 768, 1024")
    target_sizes = [512, 768, 1024]


process_images(input_directory, output_directory, target_sizes)
