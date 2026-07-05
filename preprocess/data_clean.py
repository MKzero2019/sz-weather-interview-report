"""
数据清洗、预处理代码
包含缺失值处理、异常值检测、特征工程等功能
"""

import pandas as pd
import numpy as np
import os
from scipy import stats

# 配置路径
RAW_DATA_DIR = "../data/raw"
CLEAN_DATA_DIR = "../data/clean"
RAW_DATA_FILENAME = "shenzhen_weather_raw.csv"
CLEAN_DATA_FILENAME = "shenzhen_weather_clean.csv"
DAILY_STATS_FILENAME = "shenzhen_weather_daily.csv"


class DataCleaner:
    """数据清洗类"""
    
    def __init__(self):
        """初始化数据清洗器"""
        # 创建数据目录
        os.makedirs(CLEAN_DATA_DIR, exist_ok=True)
        
        # 数据处理日志
        self.processing_log = []
    
    def log(self, message):
        """记录处理日志"""
        print(f"[数据清洗] {message}")
        self.processing_log.append(message)
    
    def load_raw_data(self):
        """
        加载原始数据
        
        Returns:
            pd.DataFrame: 原始数据
        """
        filepath = os.path.join(RAW_DATA_DIR, RAW_DATA_FILENAME)
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        df["时间"] = pd.to_datetime(df["时间"])
        self.log(f"加载原始数据: {len(df)} 条记录")
        return df
    
    def check_missing_values(self, df):
        """
        检查缺失值
        
        Args:
            df: 数据DataFrame
            
        Returns:
            dict: 各列缺失值统计
        """
        missing_stats = df.isnull().sum()
        missing_percent = (df.isnull().sum() / len(df)) * 100
        
        self.log("缺失值检查结果:")
        for col in df.columns:
            if missing_stats[col] > 0:
                self.log(f"  {col}: {missing_stats[col]} 个缺失值 ({missing_percent[col]:.2f}%)")
            else:
                self.log(f"  {col}: 无缺失值")
        
        return missing_stats
    
    def handle_missing_values(self, df, method="interpolate"):
        """
        处理缺失值
        
        Args:
            df: 数据DataFrame
            method: 处理方法
                - interpolate: 线性插值
                - ffill: 前向填充
                - bfill: 后向填充
                - mean: 均值填充
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        self.log(f"使用 {method} 方法处理缺失值")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if method == "interpolate": #方法选择 时间序列数据使用线性插值
            df = df.set_index("时间")
            df[numeric_cols] = df[numeric_cols].interpolate(method="time")
            df = df.reset_index()
        elif method == "ffill":
            df[numeric_cols] = df[numeric_cols].ffill()
        elif method == "bfill":
            df[numeric_cols] = df[numeric_cols].bfill()
        elif method == "mean":
            for col in numeric_cols:
                df[col] = df[col].fillna(df[col].mean())
        
        remaining_missing = df.isnull().sum().sum()
        self.log(f"缺失值处理完成，剩余缺失值: {remaining_missing} 个")
        
        return df
    
    def detect_outliers_iqr(self, df, column, iqr_factor=1.5):
        """
        使用IQR方法检测异常值
        
        Args:
            df: 数据DataFrame
            column: 列名
            iqr_factor: IQR因子
            
        Returns:
            tuple: (异常值索引, 下界, 上界)
        """
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - iqr_factor * IQR
        upper_bound = Q3 + iqr_factor * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].index
        
        return outliers, lower_bound, upper_bound
    
    def detect_outliers_zscore(self, df, column, threshold=3):
        """
        使用Z-score方法检测异常值
        
        Args:
            df: 数据DataFrame
            column: 列名
            threshold: Z-score阈值
            
        Returns:
            tuple: (异常值索引, 阈值)
        """
        z_scores = np.abs(stats.zscore(df[column]))
        outliers = df[z_scores > threshold].index
        
        return outliers, threshold
    
    def handle_outliers(self, df, method="clip", iqr_factor=1.5):
        """
        处理异常值
        
        Args:
            df: 数据DataFrame
            method: 处理方法
                - clip: 截断（将异常值限制在边界内）
                - remove: 删除异常值
                - interpolate: 插值替换
            iqr_factor: IQR因子
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        self.log(f"使用 {method} 方法处理异常值 (IQR因子: {iqr_factor})")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        total_outliers = 0
        
        for col in numeric_cols:
            outliers, lower, upper = self.detect_outliers_iqr(df, col, iqr_factor)
            outlier_count = len(outliers)
            total_outliers += outlier_count
            
            if outlier_count > 0:
                self.log(f"  {col}: 检测到 {outlier_count} 个异常值 (范围: [{lower:.2f}, {upper:.2f}])")
                
                if method == "clip": #方法选择
                    df[col] = df[col].clip(lower=lower, upper=upper)
                elif method == "remove":
                    df = df.drop(outliers)
                elif method == "interpolate":
                    df.loc[outliers, col] = np.nan
                    df = df.set_index("时间")
                    df[col] = df[col].interpolate(method="time")
                    df = df.reset_index()
        
        self.log(f"异常值处理完成，共处理 {total_outliers} 个异常值")
        
        return df
    
    def unify_units(self, df):
        """
        单位统一与数据格式转换
        
        Args:
            df: 数据DataFrame
            
        Returns:
            pd.DataFrame: 处理后的数据
        """
        self.log("执行单位统一与数据格式转换")
        
        # 确保时间列为datetime格式
        df["时间"] = pd.to_datetime(df["时间"])
        
        # 添加日期列（用于按天分组）
        df["日期"] = df["时间"].dt.date
        
        # 添加小时列
        df["小时"] = df["时间"].dt.hour
        
        # 添加星期几
        df["星期"] = df["时间"].dt.day_name()
        
        # 确保所有数值列为float类型
        numeric_cols = ["气温", "相对湿度", "体感温度", "降水量", "风速", "气压", "PM2.5", "PM10"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        self.log("单位统一完成，新增列: 日期、小时、星期")
        
        return df
    
    def add_derived_features(self, df):
        """
        添加衍生特征
        
        Args:
            df: 数据DataFrame
            
        Returns:
            pd.DataFrame: 添加衍生特征后的数据
        """
        self.log("添加衍生特征")
        
        # 温度与体感温度差值
        df["体感温差"] = df["体感温度"] - df["气温"]
        
        # 温度湿度指数（THI）- 简单计算
        # THI = T - 0.55*(1-RH)*(T-14.5)
        df["温湿度指数"] = df["气温"] - 0.55 * (1 - df["相对湿度"]/100) * (df["气温"] - 14.5)
        
        # 昼夜标记（6:00-18:00为白天）
        df["昼夜"] = df["小时"].apply(lambda x: "白天" if 6 <= x < 18 else "夜晚")
        
        # 降雨标记
        df["是否降雨"] = df["降水量"].apply(lambda x: "是" if x > 0 else "否")
        
        # 空气质量等级（基于PM2.5）
        def get_aqi_level(pm25):
            if pm25 <= 35:
                return "优"
            elif pm25 <= 75:
                return "良"
            elif pm25 <= 115:
                return "轻度污染"
            elif pm25 <= 150:
                return "中度污染"
            else:
                return "重度污染"
        
        df["空气质量等级"] = df["PM2.5"].apply(get_aqi_level)
        
        self.log("衍生特征添加完成: 体感温差、温湿度指数、昼夜、是否降雨、空气质量等级")
        
        return df
    
    def calculate_daily_stats(self, df):
        """
        计算每日统计数据
        
        Args:
            df: 数据DataFrame
            
        Returns:
            pd.DataFrame: 每日统计数据
        """
        self.log("计算每日统计数据")
        
        daily_stats = df.groupby("日期").agg({
            "气温": ["min", "max", "mean", "std"],
            "相对湿度": ["min", "max", "mean"],
            "体感温度": ["min", "max", "mean"],
            "降水量": "sum",
            "风速": "mean",
            "PM2.5": "mean"
        }).round(2)
        
        # 展平多级列名
        daily_stats.columns = ["_".join(col).strip() for col in daily_stats.columns.values]
        daily_stats = daily_stats.reset_index()
        
        self.log(f"每日统计数据计算完成，共 {len(daily_stats)} 天")
        
        return daily_stats
    
    def save_clean_data(self, df, daily_stats):
        """
        保存清洗后的数据
        
        Args:
            df: 小时级清洗数据
            daily_stats: 每日统计数据
        """
        data_path = os.path.join(CLEAN_DATA_DIR, CLEAN_DATA_FILENAME)
        daily_path = os.path.join(CLEAN_DATA_DIR, DAILY_STATS_FILENAME)
        
        df.to_csv(data_path, index=False, encoding="utf-8-sig")
        daily_stats.to_csv(daily_path, index=False, encoding="utf-8-sig")
        
        self.log(f"小时级数据已保存至: {data_path}")
        self.log(f"每日统计数据已保存至: {daily_path}")
    
    def run(self):
        """
        运行完整的数据清洗流程
        
        Returns:
            tuple: (小时级数据, 每日统计数据, 处理日志)
        """
        print("=" * 60)
        print("数据清洗启动")
        print("=" * 60)
        
        # 加载原始数据
        df = self.load_raw_data()
        
        # 检查缺失值
        self.check_missing_values(df)
        
        # 处理缺失值
        df = self.handle_missing_values(df, method="interpolate")
        
        # 处理异常值
        df = self.handle_outliers(df, method="clip", iqr_factor=1.5)
        
        # 单位统一与格式转换
        df = self.unify_units(df)
        
        # 添加衍生特征
        df = self.add_derived_features(df)
        
        # 计算每日统计
        daily_stats = self.calculate_daily_stats(df)
        
        # 保存清洗后的数据
        self.save_clean_data(df, daily_stats)
        
        print("=" * 60)
        print("数据清洗完成")
        print("=" * 60)
        
        return df, daily_stats, self.processing_log


if __name__ == "__main__":
    cleaner = DataCleaner()
    df, daily_stats, log = cleaner.run()
    
    print("\n清洗后数据预览:")
    print(df.head())
    print("\n每日统计预览:")
    print(daily_stats.head())
