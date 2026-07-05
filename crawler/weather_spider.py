"""
网页爬虫主程序
获取深圳历史天气和空气质量数据
"""

import requests
import pandas as pd
import os
import sys

# 导入配置
from request_config import (
    SHENZHEN_LAT, SHENZHEN_LON,
    START_DATE, END_DATE, TIMEZONE,
    WEATHER_API_URL, AIR_QUALITY_API_URL,
    HEADERS, REQUEST_TIMEOUT,
    WEATHER_VARIABLES, AIR_QUALITY_VARIABLES,
    COLUMN_MAPPING,
    RAW_DATA_DIR, RAW_DATA_FILENAME
)


class WeatherSpider:
    """天气数据爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.lat = SHENZHEN_LAT
        self.lon = SHENZHEN_LON
        self.start_date = START_DATE
        self.end_date = END_DATE
        self.timezone = TIMEZONE
        self.headers = HEADERS
        self.timeout = REQUEST_TIMEOUT
        
        # 创建数据目录
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    def fetch_weather_data(self):
        """
        获取历史天气数据
        
        Returns:
            pd.DataFrame: 天气数据DataFrame
        """
        print(f"[爬虫] 开始获取天气数据: {self.start_date} 至 {self.end_date}")
        
        # 构建请求参数
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hourly": ",".join(WEATHER_VARIABLES),
            "timezone": self.timezone
        }
        
        try:
            response = requests.get(
                WEATHER_API_URL, 
                params=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if "hourly" not in data:
                raise ValueError("API返回数据中缺少hourly字段")
            
            # 转换为DataFrame
            df = pd.DataFrame(data["hourly"])
            
            # 重命名列名
            df = df.rename(columns=COLUMN_MAPPING)
            
            # 转换时间格式
            df["时间"] = pd.to_datetime(df["时间"])
            
            print(f"[爬虫] 天气数据获取成功，共 {len(df)} 条记录")
            print(f"[爬虫] 数据时间范围: {df['时间'].min()} 至 {df['时间'].max()}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"[爬虫] 天气数据获取失败: {e}")
            raise
    
    def fetch_air_quality_data(self):
        """
        获取空气质量数据
        
        Returns:
            pd.DataFrame: 空气质量数据DataFrame
        """
        print(f"[爬虫] 开始获取空气质量数据: {self.start_date} 至 {self.end_date}")
        
        # 构建请求参数
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hourly": ",".join(AIR_QUALITY_VARIABLES),
            "timezone": self.timezone
        }
        
        try:
            response = requests.get(
                AIR_QUALITY_API_URL, 
                params=params, 
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if "hourly" not in data:
                raise ValueError("API返回数据中缺少hourly字段")
            
            # 转换为DataFrame
            df = pd.DataFrame(data["hourly"])
            
            # 重命名列名
            df = df.rename(columns=COLUMN_MAPPING)
            
            # 转换时间格式
            df["时间"] = pd.to_datetime(df["时间"])
            
            print(f"[爬虫] 空气质量数据获取成功，共 {len(df)} 条记录")
            print(f"[爬虫] 数据时间范围: {df['时间'].min()} 至 {df['时间'].max()}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"[爬虫] 空气质量数据获取失败: {e}")
            raise
    
    def merge_data(self, weather_df, air_quality_df):
        """
        合并天气数据和空气质量数据
        
        Args:
            weather_df: 天气数据DataFrame
            air_quality_df: 空气质量数据DataFrame
            
        Returns:
            pd.DataFrame: 合并后的完整数据
        """
        print("[爬虫] 合并天气数据与空气质量数据")
        
        # 按时间列合并
        merged_df = pd.merge(weather_df, air_quality_df, on="时间", how="inner")
        
        print(f"[爬虫] 合并后共 {len(merged_df)} 条记录")
        
        return merged_df
    
    def save_raw_data(self, df):
        """
        保存原始数据到CSV文件
        
        Args:
            df: 数据DataFrame
        """
        filepath = os.path.join(RAW_DATA_DIR, RAW_DATA_FILENAME)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"[爬虫] 原始数据已保存至: {filepath}")
    
    def run(self):
        """
        运行完整的爬虫流程
        
        Returns:
            pd.DataFrame: 完整的天气数据
        """
        print("=" * 60)
        print("天气数据爬虫启动")
        print("=" * 60)
        
        # 获取天气数据
        weather_df = self.fetch_weather_data()
        
        # 获取空气质量数据
        air_quality_df = self.fetch_air_quality_data()
        
        # 合并数据
        merged_df = self.merge_data(weather_df, air_quality_df)
        
        # 保存原始数据
        self.save_raw_data(merged_df)
        
        print("=" * 60)
        print("天气数据爬虫完成")
        print("=" * 60)
        
        return merged_df


if __name__ == "__main__":
    spider = WeatherSpider()
    data = spider.run()
    print("\n数据预览:")
    print(data.head())
    print("\n数据统计:")
    print(data.describe())
