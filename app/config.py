import os
from dotenv import load_dotenv

# 加载 .env 文件中的隐藏配置
load_dotenv()

# ==========================================
# 在这里统一定义所有的系统配置
# ==========================================

# 读取 API Key，如果没有读取到则默认为 None
API_KEY = os.getenv("API_KEY")
DS_API_KEY = os.getenv("DS_API_KEY")

# 读取 Base URL，可以给一个默认值（以防 .env 里没写）
BASE_URL = os.getenv("BASE_URL")
DS_BASE_URL = os.getenv("DS_BASE_URL")
# ==========================================
# 安全校验：启动时检查核心配置是否存在
# ==========================================
if not API_KEY:
    raise ValueError("严重错误：未找到 API Key！请确保项目根目录下存在 .env 文件并配置了 API_KEY。")