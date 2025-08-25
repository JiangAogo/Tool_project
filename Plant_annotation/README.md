# 植物识别与标注（本地可视化）

一个本地运行的可视化工具：  
上传图片 → 调用 **GPT-5** 返回植物清单与相对坐标（JSON） → 本地 **Pillow** 画圈编号 → 导出 PNG/JSON/CSV。

## 快速开始

1. **创建环境并安装依赖**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
