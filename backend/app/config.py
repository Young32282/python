"""应用配置"""

# 数据库配置
DB_URL = "sqlite:///./smart_store.db"

# JWT配置
JWT_SECRET = "smart-store-jwt-secret-2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 480  # 8小时

# AI大模型配置（DeepSeek）
AI_API_KEY = "sk-dd4beaeb1eb64d15880c347668f9c6e2"
AI_BASE_URL = "https://api.deepseek.com/v1"
AI_MODEL = "deepseek-chat"
AI_TIMEOUT = 5.0  # 超时秒数，超时自动降级为规则推荐
