"""
箱线图、正态分布图绘制
"""
"""
箱线图、正态分布图绘制
"""
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
import os

my_font = FontProperties(fname=r"../fonts/simhei.ttf")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 路径配置
CLEAN_DATA_DIR = "../data/clean"
CHARTS_DIR = "../report/charts"
CLEAN_DATA_FILENAME = "shenzhen_weather_clean.csv"
DAILY_STATS_FILENAME = "shenzhen_weather_daily.csv"

class BoxPlotter:
    """箱线图绘制类"""
    
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
        daily_stats["日期"] = pd.to_datetime(daily_stats["日期"]).dt.date
        
        self.log(f"加载数据: {len(df)} 条小时记录, {len(daily_stats)} 天统计")
        
        return df, daily_stats
    
    def plot_temperature_boxplot_by_day(self, df, filename="01_temperature_boxplot_by_day.png"):
        """
        绘制温度与时间（按天）的箱线图
        """
        self.log("绘制温度与时间的箱线图")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 准备数据
        days = sorted(df["日期"].unique())
        data_by_day = [df[df["日期"] == day]["气温"].values for day in days]
        x_labels = [str(d) for d in days]

        # 移除labels参数
        bp = ax.boxplot(data_by_day, patch_artist=True)
        # 手动设置横轴刻度与文字
        ax.set_xticks(range(1, len(x_labels)+1))
        ax.set_xticklabels(x_labels)
        
        # 设置颜色
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(days)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # 设置其他元素颜色
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(bp[element], color='#2c3e50', linewidth=1.5)
        
        ax.set_title('深圳每日气温分布箱线图 (2026-06-20 至 2026-07-03)', fontsize=16, fontweight='bold', pad=20, fontproperties=my_font)
        ax.set_xlabel('日期', fontsize=12, fontproperties=my_font)
        ax.set_ylabel('气温 (°C)', fontsize=12, fontproperties=my_font)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"温度箱线图已保存: {filepath}")
        return filepath
    
    def plot_temperature_distribution(self, df, filename="02_temperature_distribution.png"):
        """
        绘制温度的正态分布图（直方图+核密度估计）

        Args:
            df: 小时级数据
            filename: 输出文件名
        """
        self.log("绘制温度正态分布图")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        temp_data = df["气温"].values
        
        # 左图：直方图 + KDE
        ax1.hist(temp_data, bins=30, density=True, alpha=0.7, color='#3498db', edgecolor='white')
        
        # 核密度估计
        kde = stats.gaussian_kde(temp_data)
        x_range = np.linspace(temp_data.min() - 1, temp_data.max() + 1, 200)
        ax1.plot(x_range, kde(x_range), 'r-', linewidth=2, label='核密度估计')
        
        # 正态分布拟合
        mu, std = stats.norm.fit(temp_data)
        ax1.plot(x_range, stats.norm.pdf(x_range, mu, std), 'g--', linewidth=2, 
                label=f'正态分布 (μ={mu:.2f}, σ={std:.2f})')

        ax1.set_title('气温分布直方图与核密度估计', fontsize=14, fontweight='bold', fontproperties=my_font)
        ax1.set_xlabel('气温 (°C)', fontsize=11, fontproperties=my_font)
        ax1.set_ylabel('概率密度', fontsize=11, fontproperties=my_font)
        ax1.legend(fontsize=10, prop=my_font)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # 右图：Q-Q图
        stats.probplot(temp_data, dist="norm", plot=ax2)
        ax2.set_title('气温Q-Q图（正态性检验）', fontsize=14, fontweight='bold', fontproperties=my_font)
        ax2.set_xlabel('理论正态分位数', fontsize=11, fontproperties=my_font)
        ax2.set_ylabel('气温观测值（升序）', fontsize=11, fontproperties=my_font)
        ax2.get_lines()[0].set_markerfacecolor("#ffd500")
        ax2.get_lines()[0].set_markeredgecolor("#ffc400")
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        plt.suptitle('深圳气温分布正态性分析', fontsize=16, fontweight='bold', y=1.02, fontproperties=my_font)
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"温度分布图已保存: {filepath}")
        return filepath
    
    def plot_temp_vs_apparent_boxplot(self, df, filename="05_temp_vs_apparent_boxplot.png"):
        """
        绘制气温与体感温度对比箱线图
        """
        self.log("绘制气温与体感温度对比箱线图")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 准备数据
        data = [df["气温"].values, df["体感温度"].values]
        labels = ['气温', '体感温度']
        
        # 移除labels参数，只传数据
        bp = ax.boxplot(data, patch_artist=True, widths=0.6)
        # 手动设置x轴刻度标签
        ax.set_xticks([1, 2])
        ax.set_xticklabels(labels, fontproperties=my_font)
        
        # 设置颜色
        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # 设置其他元素颜色
        for element in ['whiskers', 'caps', 'medians']:
            plt.setp(bp[element], color='#2c3e50', linewidth=2)
        
        # 添加数值标注
        for idx, (label, values) in enumerate(zip(labels, data)):
            pos = idx + 1
            median = np.median(values)
            mean = np.mean(values)
            ax.text(pos, median, f'中位数: {median:.1f}°C', 
                ha='center', va='top', fontsize=10, fontweight='bold', fontproperties=my_font)
            ax.text(pos, mean, f'均值: {mean:.1f}°C', 
                ha='center', va='bottom', fontsize=10, color='white', fontproperties=my_font)
        
        ax.set_title('气温与体感温度对比箱线图', fontsize=16, fontweight='bold', pad=20, fontproperties=my_font)
        ax.set_ylabel('温度 (°C)', fontsize=12, fontproperties=my_font)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加差值说明
        temp_diff = df["体感温度"].mean() - df["气温"].mean()
        ax.text(0.5, 0.02, f'平均体感温差: +{temp_diff:.2f}°C', 
            transform=ax.transAxes, ha='center', fontsize=11, 
            bbox=dict(boxstyle='round', facecolor='#f1c40f', alpha=0.8), fontproperties=my_font)
        
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"气温与体感温度对比箱线图已保存: {filepath}")
        return filepath
    
    def run(self):
        """
        运行箱线图绘制流程
        
        Returns:
            dict: 生成的图表路径字典
        """
        print("=" * 60)
        print("箱线图与分布图绘制启动")
        print("=" * 60)
        
        # 加载数据
        df, daily_stats = self.load_clean_data()
        
        figures = {}
        
        # 1. 温度与时间的箱线图
        figures['temperature_boxplot'] = self.plot_temperature_boxplot_by_day(df)
        
        # 2. 温度的正态分布图
        figures['temperature_distribution'] = self.plot_temperature_distribution(df)
        
        # 3. 气温与体感温度对比箱线图
        figures['temp_vs_apparent_boxplot'] = self.plot_temp_vs_apparent_boxplot(df)
        
        print("=" * 60)
        print(f"箱线图与分布图绘制完成，共生成 {len(figures)} 张图表")
        print("=" * 60)
        
        return figures


if __name__ == "__main__":
    plotter = BoxPlotter()
    figures = plotter.run()
    
    print("\n生成的图表:")
    for name, path in figures.items():
        print(f"  {name}: {path}")
