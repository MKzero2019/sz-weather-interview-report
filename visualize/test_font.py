import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 强制只使用黑体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 打印所有可用字体
all_fonts = [f.name for f in fm.fontManager.ttflist]
print("全部字体列表：")
print(all_fonts)
print("\n是否包含SimHei：", "SimHei" in all_fonts)

# 画一张测试图验证中文
fig, ax = plt.subplots()
ax.set_title("中文测试：气温与体感温度散点图")
ax.set_xlabel("横轴：气温(℃)")
ax.set_ylabel("纵轴：体感温度(℃)")
fig.savefig("../report/charts/font_test.png", dpi=200)
print("测试图已生成 font_test.png")