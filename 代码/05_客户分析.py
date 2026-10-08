import os
from pathlib import Path


项目目录 = Path(__file__).resolve().parents[1]

客户销售文件 = (
    项目目录
    / "数据"
    / "处理后数据"
    / "客户销售.csv"
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


# 设置Matplotlib缓存位置
绘图缓存目录 = 项目目录 / ".matplotlib"
绘图缓存目录.mkdir(exist_ok=True)

os.environ["MPLCONFIGDIR"] = str(
    绘图缓存目录
)


import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

print("===== 读取客户销售数据 =====")

客户销售数据 = pd.read_csv(
    客户销售文件,
    dtype={
        "InvoiceNo": "string",
        "StockCode": "string",
        "CustomerID": "string"
    }
)

客户销售数据["InvoiceDate"] = pd.to_datetime(
    客户销售数据["InvoiceDate"],
    errors="coerce"
)

print(
    "客户交易明细：",
    len(客户销售数据)
)

print(
    "客户编号缺失：",
    客户销售数据["CustomerID"]
    .isna()
    .sum()
)

print(
    "可识别客户数量：",
    客户销售数据["CustomerID"]
    .nunique()
)
客户汇总表 = (
    客户销售数据
    .groupby(
        "CustomerID",
        as_index=False
    )
    .agg(
        首次购买时间=("InvoiceDate", "min"),
        最后购买时间=("InvoiceDate", "max"),
        购买次数=("InvoiceNo", "nunique"),
        购买商品数量=("Quantity", "sum"),
        累计消费金额=("Sales", "sum")
    )
)

客户汇总表["客户平均客单价"] = (
    客户汇总表["累计消费金额"]
    / 客户汇总表["购买次数"]
)

print("\n===== 客户汇总表示例 =====")

print(
    客户汇总表
    .head(10)
    .to_string(index=False)
)



客户总数 = len(客户汇总表)

一次性客户数量 = (
    客户汇总表["购买次数"] == 1
).sum()

复购客户数量 = (
    客户汇总表["购买次数"] >= 2
).sum()

一次性客户占比 = (
    一次性客户数量
    / 客户总数
    * 100
)

复购率 = (
    复购客户数量
    / 客户总数
    * 100
)
print("\n===== 客户复购指标 =====")

print(
    f"客户总数："
    f"{客户总数:,}"
)

print(
    f"一次性客户："
    f"{一次性客户数量:,}"
)

print(
    f"复购客户："
    f"{复购客户数量:,}"
)

print(
    f"一次性客户占比："
    f"{一次性客户占比:.2f}%"
)

print(
    f"整体复购率："
    f"{复购率:.2f}%"
)


购买1次客户 = (
    客户汇总表["购买次数"] == 1
).sum()

购买2至3次客户 = (
    客户汇总表["购买次数"]
    .between(2, 3)
).sum()

购买4至5次客户 = (
    客户汇总表["购买次数"]
    .between(4, 5)
).sum()

购买6次以上客户 = (
    客户汇总表["购买次数"] >= 6
).sum()


购买频次表 = pd.DataFrame({
    "购买频次": [
        "1次",
        "2至3次",
        "4至5次",
        "6次及以上"
    ],
    "客户数量": [
        购买1次客户,
        购买2至3次客户,
        购买4至5次客户,
        购买6次以上客户
    ]
})

购买频次表["客户占比%"] = (
    购买频次表["客户数量"]
    / 客户总数
    * 100
)

print("\n===== 客户购买频次分布 =====")
print(
    购买频次表.to_string(
        index=False
    )
)



高价值客户前十名 = (
    客户汇总表
    .sort_values(
        "累计消费金额",
        ascending=False
    )
    .head(10)
)

print("\n===== 累计消费最高的10位客户 =====")

print(
    高价值客户前十名[
        [
            "CustomerID",
            "购买次数",
            "购买商品数量",
            "累计消费金额",
            "客户平均客单价"
        ]
    ].to_string(index=False)
)


客户汇总文件 = (
    处理后数据目录
    / "客户汇总.csv"
)

购买频次文件 = (
    处理后数据目录
    / "客户购买频次.csv"
)

客户汇总表.to_csv(
    客户汇总文件,
    index=False,
    encoding="utf-8-sig"
)

购买频次表.to_csv(
    购买频次文件,
    index=False,
    encoding="utf-8-sig"
)

频次名称列表 = [
    "1 Order",
    "2-3 Orders",
    "4-5 Orders",
    "6+ Orders"
]

客户数量列表 = (
    购买频次表["客户数量"]
    .astype(int)
    .tolist()
)

图形, 坐标轴 = plt.subplots(
    figsize=(9, 6)
)

柱形 = 坐标轴.bar(
    频次名称列表,
    客户数量列表,
    color=[
        "#4E79A7",
        "#59A14F",
        "#F28E2B",
        "#E15759"
    ]
)

坐标轴.set_title(
    "Customer Purchase Frequency"
)

坐标轴.set_xlabel(
    "Purchase Frequency"
)

坐标轴.set_ylabel(
    "Number of Customers"
)

坐标轴.grid(
    axis="y",
    alpha=0.25
)


# 在每根柱形上显示客户数量
for 单个柱形 in 柱形:
    高度 = 单个柱形.get_height()

    坐标轴.text(
        单个柱形.get_x()
        + 单个柱形.get_width() / 2,
        高度,
        f"{int(高度):,}",
        ha="center",
        va="bottom"
    )


图形.tight_layout()

购买频次图表文件 = (
    图表目录
    / "客户购买频次.png"
)

图形.savefig(
    购买频次图表文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)



print("\n===== 客户分析完成 =====")

print("客户汇总数据：", 客户汇总文件)
print("购买频次数据：", 购买频次文件)
print("购买频次图表：", 购买频次图表文件)
