import os
import openpyxl
from openpyxl.drawing.image import Image
from openpyxl.utils import get_column_letter

# 获取图片文件夹路径
图片文件夹路径 = input("请输入图片文件夹路径：")

# 获取Excel文件路径
excel文件路径 = input("请输入Excel文件路径：")

# 加载Excel工作簿
工作簿 = openpyxl.load_workbook(excel文件路径)

# 选择活动工作表
工作表 = 工作簿.active

# 定义每个Excel单元格的默认像素尺寸（1个单元格宽度大约为7个像素，行高度单位为像素）
def 设置列宽(工作表, 列, 像素宽度):
    列宽 = 像素宽度 / 7  # 每个Excel列大约为7个像素宽
    工作表.column_dimensions[列].width = 列宽

def 设置行高(工作表, 行, 像素高度):
    工作表.row_dimensions[行].height = 像素高度  # 行高直接以像素为单位设置

# 图片缩放比例
缩放比例 = 0.4  # 例如，缩放至原始大小的50%

# 遍历图片文件夹中的图片
for 行号, 图片文件名 in enumerate(os.listdir(图片文件夹路径), start=1):
    if 图片文件名.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        图片路径 = os.path.join(图片文件夹路径, 图片文件名)
        
        # 创建图片对象
        图片 = Image(图片路径)
        
        # 获取图片原始尺寸
        图片宽度, 图片高度 = 图片.width, 图片.height
        
        # 调整图片尺寸（根据缩放比例）
        图片.width = 图片宽度 * 缩放比例
        图片.height = 图片高度 * 缩放比例
        
        # 调整列宽和行高匹配图片尺寸
        列号 = 'G'  # 假设图片始终插入列 F
        设置列宽(工作表, 列号, 图片.width)
        设置行高(工作表, 行号, 图片.height)
        
        # 将图片插入到对应的单元格
        工作表.add_image(图片, f'G{行号}')

# 保存Excel文件
工作簿.save(excel文件路径)

print("图片已成功插入并调整单元格大小到Excel文件中。")
