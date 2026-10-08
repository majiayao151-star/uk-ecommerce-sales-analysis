import os
from pathlib import Path


# 找到“电商销售分析”项目目录
项目目录 = Path(__file__).resolve().parents[1]

正常销售文件 = (
    项目目录
    / "数据"
    / "处理后数据"
    / "正常销售.csv"
)

处理后数据目录 = (
    项目目录
    / "数据"
    / "处理后数据"
)

图表目录 = 项目目录 / "图表"

图表目录.mkdir(
    parents=True,
    exist_ok=True
)


# 把Matplotlib缓存保存在项目中
绘图缓存目录 = 项目目录 / ".matplotlib"
绘图缓存目录.mkdir(exist_ok=True)

os.environ["MPLCONFIGDIR"] = str(
    绘图缓存目录
)


import pandas as pd
import matplotlib

# 使用后台绘图，避免IDLE图形窗口冲突
matplotlib.use("Agg")

import matplotlib.pyplot as plt

print("===== 读取正常销售数据 =====")

销售数据 = pd.read_csv(
    正常销售文件,
    dtype={
        "InvoiceNo": "string",
        "StockCode": "string",
        "CustomerID": "string"
    }
)

销售数据["InvoiceDate"] = pd.to_datetime(
    销售数据["InvoiceDate"],
    errors="coerce"
)

print("销售明细行数：", len(销售数据))
print(
    "日期范围：",
    销售数据["InvoiceDate"].min(),
    "至",
    销售数据["InvoiceDate"].max()
)

总销售额 = (
    销售数据["Sales"]
    .sum()
)

订单数量 = (
    销售数据["InvoiceNo"]
    .nunique()
)

可识别客户数量 = (
    销售数据["CustomerID"]
    .nunique()
)

商品销售数量 = (
    销售数据["Quantity"]
    .sum()
)

平均客单价 = (
    总销售额
    / 订单数量
)

平均每单商品数 = (
    商品销售数量
    / 订单数量
)




print("\n===== 核心销售指标 =====")

print(
    f"正常销售额："
    f"£{总销售额:,.2f}"
)

print(
    f"正常订单数量："
    f"{订单数量:,}"
)

print(
    f"可识别客户数量："
    f"{可识别客户数量:,}"
)

print(
    f"商品销售数量："
    f"{商品销售数量:,}"
)

print(
    f"平均客单价："
    f"£{平均客单价:,.2f}"
)

print(
    f"平均每单商品数："
    f"{平均每单商品数:,.2f}"
)



核心指标表 = pd.DataFrame({
    "指标": [
        "正常销售额",
        "正常订单数量",
        "可识别客户数量",
        "商品销售数量",
        "平均客单价",
        "平均每单商品数"
    ],
    "数值": [
        总销售额,
        订单数量,
        可识别客户数量,
        商品销售数量,
        平均客单价,
        平均每单商品数
    ]
})



销售数据["YearMonth"] = (
    销售数据["InvoiceDate"]
    .dt.to_period("M")
    .astype("string")
)

月度销售表 = (
    销售数据
    .groupby(
        "YearMonth",
        as_index=False
    )
    .agg(
        销售额=("Sales", "sum"),
        订单数=("InvoiceNo", "nunique"),
        客户数=("CustomerID", "nunique"),
        商品数量=("Quantity", "sum")
    )
    .sort_values("YearMonth")
)

月度销售表["平均客单价"] = (
    月度销售表["销售额"]
    / 月度销售表["订单数"]
)




最后交易日期 = (
    销售数据["InvoiceDate"]
    .max()
)

最后月份 = (
    月度销售表["YearMonth"]
    .max()
)

最后月份不完整 = (
    最后交易日期.day
    < 最后交易日期.days_in_month
)

月度销售表["是否不完整月份"] = False

if 最后月份不完整:
    月度销售表.loc[
        月度销售表["YearMonth"] == 最后月份,
        "是否不完整月份"
    ] = True



完整月份数据 = 月度销售表[
    ~月度销售表["是否不完整月份"]
].copy()

最佳月份记录 = 完整月份数据.loc[
    完整月份数据["销售额"].idxmax()
]

print("\n===== 月度销售表现 =====")
print(月度销售表.to_string(index=False))

print("\n销售额最高的完整月份：")
print("月份：", 最佳月份记录["YearMonth"])

print(
    "销售额：£",
    round(
        最佳月份记录["销售额"],
        2
    )
)

print(
    "\n注意：",
    最后月份,
    "是不完整月份，不参与最佳月份比较。"
)


核心指标文件 = (
    处理后数据目录
    / "销售核心指标.csv"
)

月度销售文件 = (
    处理后数据目录
    / "月度销售.csv"
)

核心指标表.to_csv(
    核心指标文件,
    index=False,
    encoding="utf-8-sig"
)

月度销售表.to_csv(
    月度销售文件,
    index=False,
    encoding="utf-8-sig"
)



柱形颜色 = []

for 是否不完整 in 月度销售表["是否不完整月份"]:
    if 是否不完整:
        柱形颜色.append("#F28E2B")
    else:
        柱形颜色.append("#4E79A7")


图形, 坐标轴 = plt.subplots(
    2,
    1,
    figsize=(13, 9),
    sharex=True
)


# 第一张图：月度销售额
坐标轴[0].bar(
    月度销售表["YearMonth"],
    月度销售表["销售额"],
    color=柱形颜色
)

坐标轴[0].set_title(
    "Monthly Sales"
)

坐标轴[0].set_ylabel(
    "Sales Amount (£)"
)

坐标轴[0].grid(
    axis="y",
    alpha=0.25
)


# 第二张图：月度订单量
坐标轴[1].bar(
    月度销售表["YearMonth"],
    月度销售表["订单数"],
    color=柱形颜色
)

坐标轴[1].set_title(
    "Monthly Orders"
)

坐标轴[1].set_xlabel(
    "Month"
)

坐标轴[1].set_ylabel(
    "Orders"
)

坐标轴[1].grid(
    axis="y",
    alpha=0.25
)

坐标轴[1].tick_params(
    axis="x",
    rotation=45
)


图形.text(
    0.99,
    0.01,
    "Orange = partial month",
    ha="right",
    color="#F28E2B"
)

图形.tight_layout(
    rect=(0, 0.03, 1, 1)
)


月度图表文件 = (
    图表目录
    / "月度销售概览.png"
)

图形.savefig(
    月度图表文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)




print("\n===== 分析完成 =====")
print("销售核心指标：", 核心指标文件)
print("月度销售数据：", 月度销售文件)
print("月度销售图表：", 月度图表文件)
