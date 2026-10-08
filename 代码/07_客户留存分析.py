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


绘图缓存目录 = 项目目录 / ".matplotlib"
绘图缓存目录.mkdir(exist_ok=True)

os.environ["MPLCONFIGDIR"] = str(
    绘图缓存目录
)


import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
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

print("客户交易明细：", len(客户销售数据))
print(
    "可识别客户数量：",
    客户销售数据["CustomerID"]
    .nunique()
)
print(
    "交易日期范围：",
    客户销售数据["InvoiceDate"].min(),
    "至",
    客户销售数据["InvoiceDate"].max()
)
客户销售数据["交易月份"] = (
    客户销售数据["InvoiceDate"]
    .dt.to_period("M")
)

print("\n===== 交易月份示例 =====")

print(
    客户销售数据[
        [
            "InvoiceDate",
            "交易月份"
        ]
    ]
    .head()
    .to_string(index=False)
)

客户首次购买月份 = (
    客户销售数据
    .groupby("CustomerID")["交易月份"]
    .min()
    .rename("首次购买月份")
)


客户销售数据 = (
    客户销售数据
    .merge(
        客户首次购买月份,
        on="CustomerID",
        how="left"
    )
)

print("\n===== 首次购买月份示例 =====")

print(
    客户销售数据[
        [
            "CustomerID",
            "交易月份",
            "首次购买月份"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


年份差 = (
    客户销售数据["交易月份"].dt.year
    - 客户销售数据["首次购买月份"].dt.year
)

月份差 = (
    客户销售数据["交易月份"].dt.month
    - 客户销售数据["首次购买月份"].dt.month
)

客户销售数据["客户生命周期月份"] = (
    年份差 * 12
    + 月份差
    + 1
)


print("\n===== 客户生命周期月份示例 =====")

print(
    客户销售数据[
        [
            "CustomerID",
            "交易月份",
            "首次购买月份",
            "客户生命周期月份"
        ]
    ]
    .head(15)
    .to_string(index=False)
)


留存客户数量表 = (
    客户销售数据
    .groupby(
        [
            "首次购买月份",
            "客户生命周期月份"
        ]
    )["CustomerID"]
    .nunique()
    .unstack()
)



每组初始客户数 = (
    留存客户数量表[1]
)

客户留存率表 = (
    留存客户数量表
    .divide(
        每组初始客户数,
        axis=0
    )
    * 100
)



print("\n===== 留存客户数量 =====")

print(
    留存客户数量表.to_string()
)

print("\n===== 客户留存率 =====")

print(
    客户留存率表
    .round(2)
    .to_string()
)


留存客户数量文件 = (
    处理后数据目录
    / "留存客户数量.csv"
)

客户留存率文件 = (
    处理后数据目录
    / "客户留存率.csv"
)

留存客户数量表.to_csv(
    留存客户数量文件,
    encoding="utf-8-sig"
)

客户留存率表.to_csv(
    客户留存率文件,
    encoding="utf-8-sig"
)


热力图数据 = (
    客户留存率表
    .copy()
)

热力图数据.index = (
    热力图数据.index
    .astype(str)
)


图形, 坐标轴 = plt.subplots(
    figsize=(15, 8)
)

sns.heatmap(
    热力图数据,
    mask=热力图数据.isna(),
    annot=True,
    fmt=".1f",
    cmap="Blues",
    linewidths=0.5,
    vmin=0,
    vmax=100,
    ax=坐标轴
)

坐标轴.set_title(
    "Monthly Customer Retention Rate (%)"
)

坐标轴.set_xlabel(
    "Months Since First Purchase"
)

坐标轴.set_ylabel(
    "First Purchase Month"
)

图形.tight_layout()

留存热力图文件 = (
    图表目录
    / "客户留存热力图.png"
)

图形.savefig(
    留存热力图文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)


print("\n===== 留存分析完成 =====")

print(
    "留存客户数量：",
    留存客户数量文件
)

print(
    "客户留存率：",
    客户留存率文件
)

print(
    "留存热力图：",
    留存热力图文件
)
