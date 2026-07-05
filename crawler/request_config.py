"""
请求配置文件
存放请求头、URL、API参数等配置
"""

# 深圳经纬度
SHENZHEN_LAT = 22.5431
SHENZHEN_LON = 114.0579

# 时间范围
START_DATE = "2026-06-20"
END_DATE = "2026-07-03"

# 时区
TIMEZONE = "Asia/Shanghai"

# Open-Meteo API 地址
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"
AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# 请求头配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

# 请求超时时间
REQUEST_TIMEOUT = 30

# 需要获取的天气指标
WEATHER_VARIABLES = [
    "temperature_2m",        # 2米气温 (°C)
    "relative_humidity_2m",  # 2米相对湿度 (%)
    "apparent_temperature",  # 体感温度 (°C)
    "precipitation",         # 降水量 (mm)
    "wind_speed_10m",        # 10米风速 (km/h)
    "surface_pressure",      # 地表气压 (hPa)
]

# 需要获取的空气质量指标
AIR_QUALITY_VARIABLES = [
    "pm2_5",   # PM2.5 (μg/m³)
    "pm10",    # PM10 (μg/m³)
]

# 列名映射（英文 -> 中文）
COLUMN_MAPPING = {
    "time": "时间",
    "temperature_2m": "气温",
    "relative_humidity_2m": "相对湿度",
    "apparent_temperature": "体感温度",
    "precipitation": "降水量",
    "wind_speed_10m": "风速",
    "surface_pressure": "气压",
    "pm2_5": "PM2.5",
    "pm10": "PM10"
}

# 原始数据保存路径
RAW_DATA_DIR = "../data/raw"
RAW_DATA_FILENAME = "shenzhen_weather_raw.csv"
