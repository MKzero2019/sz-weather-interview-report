"""
折线图、散点图绘制
"""

import matplotlib
matplotlib.use('Agg')  

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates
import seaborn as sns
import os

# 加载本地黑体字体（和cpk文件统一路径）
my_font = FontProperties(fname=r"../fonts/simhei.ttf")
# 兜底全局设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置路径
CLEAN_DATA_DIR = "../data/clean"
CHARTS_DIR = "../report/charts"
CLEAN_DATA_FILENAME = "shenzhen_weather_clean.csv"
DAILY_STATS_FILENAME = "shenzhen_weather_daily.csv"


class LineScatterPlotter:
    """折线图与散点图绘制类"""
    
    def __init__(self):
        """初始化绘图器"""
        # 创建图表目录
        os.makedirs(CHARTS_DIR, exist_ok=True)
        
        # 设置风格
        sns.set_style("whitegrid")
    
    def log(self, message):
        """记录日志"""
        print(f"[绘图] {message}")
    
    def load_clean_data(self):
        """
        加载清洗后的数据
        
        Returns:
            tuple: (小时级数据, 每日统计数据)
        """
        data_path = os.path.join(CLEAN_DATA_DIR, CLEAN_DATA_FILENAME)
        daily_path = os.path.join(CLEAN_DATA_DIR, DAILY_STATS_FILENAME)
        
        df = pd.read_csv(data_path, encoding="utf-8-sig")
        df["时间"] = pd.to_datetime(df["时间"])
        df["日期"] = pd.to_datetime(df["日期"]).dt.date
        
        daily_stats = pd.read_csv(daily_path, encoding="utf-8-sig")
        daily_stats["日期"] = pd.to_datetime(daily_stats["日期"])
        
        self.log(f"加载数据: {len(df)} 条小时记录, {len(daily_stats)} 天统计")
        
        return df, daily_stats
    
    def plot_temperature_scatter(self, df, filename="03_temperature_scatter.png"):
        """
        绘制温度散点图（气温 vs 体感温度）
        
        Args:
            df: 小时级数据
            filename: 输出文件名
        """
        self.log("绘制温度散点图")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 按昼夜分组绘制
        day_data = df[df["昼夜"] == "白天"]
        night_data = df[df["昼夜"] == "夜晚"]
        
        scatter_day = ax.scatter(day_data["气温"], day_data["体感温度"], 
                                c='#e67e22', alpha=0.6, s=50, label='白天', edgecolors='white', linewidth=0.5)
        scatter_night = ax.scatter(night_data["气温"], night_data["体感温度"], 
                                  c='#3498db', alpha=0.6, s=50, label='夜晚')
        
        # 添加对角线
        min_val = min(df["气温"].min(), df["体感温度"].min()) - 1
        max_val = max(df["气温"].max(), df["体感温度"].max()) + 1
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x 参考线')
        
        # 添加趋势线
        z = np.polyfit(df["气温"], df["体感温度"], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(min_val, max_val, 100)
        ax.plot(x_trend, p(x_trend), 'r-', linewidth=2, label=f'趋势线 (y={z[0]:.2f}x+{z[1]:.2f})')
        
        # 计算相关系数
        corr = df["气温"].corr(df["体感温度"])
        
        ax.set_title(f'气温与体感温度散点图 (相关系数: {corr:.4f})', fontsize=16, fontweight='bold', pad=20, fontproperties=my_font)
        ax.set_xlabel('气温 (°C)', fontsize=12, fontproperties=my_font)
        ax.set_ylabel('体感温度 (°C)', fontsize=12, fontproperties=my_font)
        ax.legend(fontsize=10, prop=my_font)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')
        
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"温度散点图已保存: {filepath}")
        return filepath
    
    def plot_temperature_line(self, df, daily_stats, filename="04_temperature_line.png"):
        """
        绘制温度折线图
        
        Args:
            df: 小时级数据
            daily_stats: 每日统计数据
            filename: 输出文件名
        """
        self.log("绘制温度折线图")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[2, 1])
        
        # 上图：小时级温度变化
        ax1.plot(df["时间"], df["气温"], color='#3498db', linewidth=1, alpha=0.7, label='小时气温')
        ax1.plot(df["时间"], df["体感温度"], color='#e74c3c', linewidth=1, alpha=0.7, label='体感温度')
        
        # 添加每日均值
        ax1.plot(daily_stats["日期"], daily_stats["气温_mean"], color='#2c3e50', 
                linewidth=2, marker='o', markersize=4, label='日均气温')
        
        ax1.set_title('深圳气温变化趋势图', fontsize=16, fontweight='bold', pad=20, fontproperties=my_font)
        ax1.set_ylabel('温度 (°C)', fontsize=12, fontproperties=my_font)
        ax1.legend(fontsize=10, loc='upper right', prop=my_font)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        # 下图：每日温度范围
        ax2.fill_between(daily_stats["日期"], daily_stats["气温_min"], daily_stats["气温_max"], 
                        alpha=0.3, color='#3498db', label='日温度范围')
        ax2.plot(daily_stats["日期"], daily_stats["气温_mean"], color='#2c3e50', 
                linewidth=2, marker='o', markersize=6, label='日均温')
        
        ax2.set_xlabel('日期', fontsize=12, fontproperties=my_font)
        ax2.set_ylabel('温度 (°C)', fontsize=12, fontproperties=my_font)
        ax2.set_title('每日温度范围', fontsize=14, fontweight='bold', fontproperties=my_font)
        ax2.legend(fontsize=10, prop=my_font)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"温度折线图已保存: {filepath}")
        return filepath
    
    def plot_correlation_heatmap(self, df, filename="07_correlation_heatmap.png"):
        """
        绘制相关性热力图
        
        Args:
            df: 小时级数据
            filename: 输出文件名
        """
        self.log("绘制相关性热力图")
        
        # 选择数值列
        numeric_cols = ["气温", "相对湿度", "体感温度", "降水量", "风速", "气压", "PM2.5", "PM10", "体感温差", "温湿度指数"]
        corr_data = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 绘制热力图
        sns.heatmap(corr_data, annot=True, fmt='.3f', cmap='RdBu_r', 
                   center=0, square=True, linewidths=0.5, 
                   cbar_kws={"shrink": 0.8}, ax=ax)
        
        ax.set_title('气象指标相关性热力图', fontsize=16, fontweight='bold', pad=20, fontproperties=my_font)
        plt.xticks(rotation=45, ha='right', fontproperties=my_font)
        plt.yticks(rotation=0, fontproperties=my_font)
        
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"相关性热力图已保存: {filepath}")
        return filepath
    
    def run(self):
        """
        运行折线图与散点图绘制流程
        
        Returns:
            dict: 生成的图表路径字典
        """
        print("=" * 60)
        print("折线图与散点图绘制启动")
        print("=" * 60)
        
        # 加载数据
        df, daily_stats = self.load_clean_data()
        
        figures = {}
        
        # 1. 温度散点图
        figures['temperature_scatter'] = self.plot_temperature_scatter(df)
        
        # 2. 温度折线图
        figures['temperature_line'] = self.plot_temperature_line(df, daily_stats)
        
        # 3. 相关性热力图
        figures['correlation_heatmap'] = self.plot_correlation_heatmap(df)
        
        print("=" * 60)
        print(f"折线图与散点图绘制完成，共生成 {len(figures)} 张图表")
        print("=" * 60)
        
        return figures


if __name__ == "__main__":
    plotter = LineScatterPlotter()
    figures = plotter.run()
    
    print("\n生成的图表:")
    for name, path in figures.items():
        print(f"  {name}: {path}")