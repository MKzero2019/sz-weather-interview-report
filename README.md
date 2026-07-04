# sz-weather-interview-report
深圳近两周气象爬虫与统计分析 | 面试二面作业项目

## 项目背景
企业二面作业：爬取深圳近两周气象数据（气温、湿度、体感温度、PM2.5等），完成数据清洗、多维度可视化图表、CPK过程能力分析，输出完整数据分析报告。

## 技术栈
- 爬虫：requests + BeautifulSoup4
- 数据处理：Pandas / Numpy
- 可视化：Matplotlib + Seaborn
- 统计分析：Scipy（正态分布检验、CPK计算）

## 项目模块
1. crawler：网页数据爬取，获取原始气象数据
2. preprocess：缺失值、异常值、单位统一等数据预处理
3. visualize：箱线图、折线图、散点图、正态分布图、CPK分析绘图
4. report：完整面试分析报告，含代码说明、图表解读、季节结论

## 运行说明
1. 安装依赖：pip install -r requirements.txt
2. 执行爬虫：python crawler/weather_spider.py
3. 数据清洗：python preprocess/data_clean.py
4. 生成全部图表：python visualize/下各绘图脚本