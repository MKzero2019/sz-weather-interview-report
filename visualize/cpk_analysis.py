"""
CPK过程能力分析
包含CPK计算和可视化
"""

import matplotlib
matplotlib.use('Agg')  

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
from scipy import stats
import os

# 加载本地黑体字体
my_font = FontProperties(fname=r"../fonts/simhei.ttf")
# 兜底全局配置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置路径
CLEAN_DATA_DIR = "../data/clean"
CHARTS_DIR = "../report/charts"
CLEAN_DATA_FILENAME = "shenzhen_weather_clean.csv"

# CPK分析规格（温度与湿度）
# 以深圳夏季舒适标准作为参考
TEMP_USL = 35.0  # 温度规格上限 (°C)
TEMP_LSL = 20.0  # 温度规格下限 (°C)
HUMIDITY_USL = 90.0  # 湿度规格上限 (%)
HUMIDITY_LSL = 40.0  # 湿度规格下限 (%)
CPK_THRESHOLD = 1.33  # CPK合格阈值


class CPKAnalyzer:
    """CPK分析类"""
    
    def __init__(self):
        """初始化CPK分析器"""
        # 创建图表目录
        os.makedirs(CHARTS_DIR, exist_ok=True)
        
        sns.set_style("whitegrid")
        
        # CPK结果
        self.cpk_results = {}
    
    def log(self, message):
        """记录日志"""
        print(f"[CPK分析] {message}")
    
    def load_clean_data(self):
        """
        加载清洗后的数据
        
        Returns:
            pd.DataFrame: 小时级数据
        """
        data_path = os.path.join(CLEAN_DATA_DIR, CLEAN_DATA_FILENAME)
        
        df = pd.read_csv(data_path, encoding="utf-8-sig")
        df["时间"] = pd.to_datetime(df["时间"])
        
        self.log(f"加载数据: {len(df)} 条小时记录")
        
        return df
    
    def calculate_cpk(self, data, usl, lsl):
        """
        计算CPK值
        
        Args:
            data: 数据数组
            usl: 规格上限
            lsl: 规格下限
            
        Returns:
            tuple: (cpk, cp, cpu, cpl, mean, std)
        """
        mean = np.mean(data) #numpy输出完整公式
        std = np.std(data, ddof=1)  # 样本标准差
        
        # 计算CP、CPU和CPL
        cp = (usl - lsl) / (6 * std)
        
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        
        # CPK取最小值
        cpk = min(cpu, cpl)
        
        return cpk, cp, cpu, cpl, mean, std
    
    def plot_cpk_analysis(self, df, filename="06_cpk_analysis.png"):
        """
        绘制温度与湿度的CPK分析图
        
        Args:
            df: 小时级数据
            filename: 输出文件名
        """
        self.log("绘制CPK分析图")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # ========== 温度CPK分析 ==========
        temp_data = df["气温"].values
        temp_cpk, temp_cp, temp_cpu, temp_cpl, temp_mean, temp_std = self.calculate_cpk(
            temp_data, TEMP_USL, TEMP_LSL
        )
        
        # 保存结果
        self.cpk_results['temperature'] = {
            'cpk': temp_cpk, 'cp': temp_cp, 
            'cpu': temp_cpu, 'cpl': temp_cpl,
            'mean': temp_mean, 'std': temp_std,
            'usl': TEMP_USL, 'lsl': TEMP_LSL
        }
        
        # 绘制直方图
        n, bins, patches = ax1.hist(temp_data, bins=30, density=True, alpha=0.7, 
                                   color='#3498db', edgecolor='white')
        
        # 绘制正态分布曲线
        x = np.linspace(TEMP_LSL - 2*temp_std, TEMP_USL + 2*temp_std, 200)
        ax1.plot(x, stats.norm.pdf(x, temp_mean, temp_std), 'r-', linewidth=2, label='正态分布')
        
        # 绘制规格线
        ax1.axvline(x=TEMP_LSL, color='green', linestyle='--', linewidth=2, label=f'规格下限 LSL={TEMP_LSL}°C')
        ax1.axvline(x=TEMP_USL, color='red', linestyle='--', linewidth=2, label=f'规格上限 USL={TEMP_USL}°C')
        ax1.axvline(x=temp_mean, color='orange', linestyle='-', linewidth=2, label=f'均值 μ={temp_mean:.2f}°C')
        
        # 添加CPK信息
        status = "合格" if temp_cpk >= CPK_THRESHOLD else "不合格"
        
        info_text = f"""
        CPK = {temp_cpk:.4f}  {status}
        CP = {temp_cp:.4f}
        CPU = {temp_cpu:.4f}
        CPL = {temp_cpl:.4f}
        均值 μ = {temp_mean:.2f}°C
        标准差 σ = {temp_std:.2f}°C
        """
        
        ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                fontproperties=my_font)
        
        ax1.set_title(f'气温CPK分析 (规格范围: {TEMP_LSL}°C - {TEMP_USL}°C)', 
                     fontsize=14, fontweight='bold', fontproperties=my_font)
        ax1.set_xlabel('气温 (°C)', fontsize=11, fontproperties=my_font)
        ax1.set_ylabel('概率密度', fontsize=11, fontproperties=my_font)
        ax1.legend(fontsize=9, loc='upper right', prop=my_font)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # ========== 湿度CPK分析 ==========
        humidity_data = df["相对湿度"].values
        hum_cpk, hum_cp, hum_cpu, hum_cpl, hum_mean, hum_std = self.calculate_cpk(
            humidity_data, HUMIDITY_USL, HUMIDITY_LSL
        )
        
        # 保存结果
        self.cpk_results['humidity'] = {
            'cpk': hum_cpk, 'cp': hum_cp,
            'cpu': hum_cpu, 'cpl': hum_cpl,
            'mean': hum_mean, 'std': hum_std,
            'usl': HUMIDITY_USL, 'lsl': HUMIDITY_LSL
        }
        
        # 绘制直方图
        n, bins, patches = ax2.hist(humidity_data, bins=30, density=True, alpha=0.7, 
                                   color='#2ecc71', edgecolor='white')
        
        # 绘制正态分布曲线
        x = np.linspace(HUMIDITY_LSL - 2*hum_std, HUMIDITY_USL + 2*hum_std, 200)
        ax2.plot(x, stats.norm.pdf(x, hum_mean, hum_std), 'r-', linewidth=2, label='正态分布')
        
        # 绘制规格线
        ax2.axvline(x=HUMIDITY_LSL, color='green', linestyle='--', linewidth=2, 
                   label=f'规格下限 LSL={HUMIDITY_LSL}%')
        ax2.axvline(x=HUMIDITY_USL, color='red', linestyle='--', linewidth=2, 
                   label=f'规格上限 USL={HUMIDITY_USL}%')
        ax2.axvline(x=hum_mean, color='orange', linestyle='-', linewidth=2, 
                   label=f'均值 μ={hum_mean:.2f}%')
        
        # 添加CPK信息
        status = "合格" if hum_cpk >= CPK_THRESHOLD else "不合格"
        
        info_text = f"""
        CPK = {hum_cpk:.4f}  {status}
        CP = {hum_cp:.4f}
        CPU = {hum_cpu:.4f}
        CPL = {hum_cpl:.4f}
        均值 μ = {hum_mean:.2f}%
        标准差 σ = {hum_std:.2f}%
        """
        
        ax2.text(0.02, 0.98, info_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                fontproperties=my_font)
        
        ax2.set_title(f'相对湿度CPK分析 (规格范围: {HUMIDITY_LSL}% - {HUMIDITY_USL}%)', 
                     fontsize=14, fontweight='bold', fontproperties=my_font)
        ax2.set_xlabel('相对湿度 (%)', fontsize=11, fontproperties=my_font)
        ax2.set_ylabel('概率密度', fontsize=11, fontproperties=my_font)
        ax2.legend(fontsize=9, loc='upper right', prop=my_font)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        plt.suptitle(f'深圳春夏季节温湿度CPK分析 (CPK合格标准: ≥{CPK_THRESHOLD})', 
                    fontsize=16, fontweight='bold', y=0.995, fontproperties=my_font)
        plt.tight_layout()
        
        filepath = os.path.join(CHARTS_DIR, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log(f"CPK分析图已保存: {filepath}")
        
        return filepath
    
    def print_cpk_summary(self):
        """打印CPK分析摘要"""
        print("\n" + "=" * 60)
        print("CPK分析结果摘要")
        print("=" * 60)
        
        if 'temperature' in self.cpk_results:
            temp = self.cpk_results['temperature']
            status = "合格" if temp['cpk'] >= CPK_THRESHOLD else "不合格"
            print(f"\n温度CPK分析:")
            print(f"  CPK: {temp['cpk']:.4f} ({status})")
            print(f"  CP:  {temp['cp']:.4f}")
            print(f"  CPU: {temp['cpu']:.4f}")
            print(f"  CPL: {temp['cpl']:.4f}")
            print(f"  均值: {temp['mean']:.2f}°C")
            print(f"  标准差: {temp['std']:.2f}°C")
            print(f"  规格范围: {temp['lsl']}°C - {temp['usl']}°C")
        
        if 'humidity' in self.cpk_results:
            hum = self.cpk_results['humidity']
            status = "合格" if hum['cpk'] >= CPK_THRESHOLD else "不合格"
            print(f"\n湿度CPK分析:")
            print(f"  CPK: {hum['cpk']:.4f} ({status})")
            print(f"  CP:  {hum['cp']:.4f}")
            print(f"  CPU: {hum['cpu']:.4f}")
            print(f"  CPL: {hum['cpl']:.4f}")
            print(f"  均值: {hum['mean']:.2f}%")
            print(f"  标准差: {hum['std']:.2f}%")
            print(f"  规格范围: {hum['lsl']}% - {hum['usl']}%")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """
        运行完整的CPK分析流程
        
        Returns:
            tuple: (图表路径, CPK结果字典)
        """
        print("=" * 60)
        print("CPK过程能力分析启动")
        print("=" * 60)
        
        # 加载数据
        df = self.load_clean_data()
        
        # 绘制CPK分析图
        cpk_chart = self.plot_cpk_analysis(df)
        
        # 打印摘要
        self.print_cpk_summary()
        
        print("=" * 60)
        print("CPK分析完成")
        print("=" * 60)
        
        return cpk_chart, self.cpk_results

if __name__ == "__main__":
    analyzer = CPKAnalyzer()
    chart_path, cpk_results = analyzer.run()
    
    print(f"\nCPK分析图: {chart_path}")