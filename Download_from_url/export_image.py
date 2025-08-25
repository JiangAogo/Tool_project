import pandas as pd
import requests
import os
from urllib.parse import urlparse
from pathlib import Path

# 读取Excel文件
df = pd.read_excel(r'C:\Users\H\Desktop\imgurl.xlsx')

# 创建保存图片的目录
save_dir = Path(r'C:\Users\H\Desktop\img\download_from_url\download_img')
save_dir.mkdir(parents=True, exist_ok=True)

# 遍历select_pic列的每一行
for index, url in enumerate(df['generated_url'], start=2):
    try:
        # 发送GET请求获取图片内容
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出异常
        
        # 解析URL，获取文件扩展名
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1]
        if not file_extension:
            file_extension = '.webp'  # 如果无法获取扩展名，默认使用.webp
        
        # 构建保存路径
        save_path = save_dir / f"{index}{file_extension}"
        
        # 保存图片
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"成功下载并保存图片: {save_path}")
    except Exception as e:
        print(f"下载第{index}张图片时出错: {str(e)}")

print("所有图片下载完成")
