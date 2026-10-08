import os
from pathlib import Path


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
    "国家数量：",
    销售数据["Country"].nunique()
)



国家销售表 = (
    销售数据
    .groupby(
        "Country",
        as_index=False
    )
    .agg(
        销售额=("Sales", "sum"),
        订单数=("InvoiceNo", "nunique"),
        客户数=("CustomerID", "nunique"),
        商品数量=("Quantity", "sum")
    )
)


国家销售表["平均客单价"] = (
    国家销售表["销售额"]
    / 国家销售表["订单数"]
)

总销售额 = (
    国家销售表["销售额"]
    .sum()
)

国家销售表["销售额占比%"] = (
    国家销售表["销售额"]
    / 总销售额
    * 100
)

国家销售表 = (
    国家销售表
    .sort_values(
        "销售额",
        ascending=False
    )
    .reset_index(drop=True)
)


print("\n===== 销售额最高的10个国家 =====")

print(
    国家销售表[
        [
            "Country",
            "销售额",
            "订单数",
            "客户数",
            "平均客单价",
            "销售额占比%"
        ]
    ]
    .head(10)
    .to_string(index=False)
)



英国记录 = 国家销售表[
    国家销售表["Country"]
    == "United Kingdom"
].iloc[0]

print("\n===== 英国市场 =====")

print(
    f"英国销售额："
    f"£{英国记录['销售额']:,.2f}"
)

print(
    f"英国订单数："
    f"{int(英国记录['订单数']):,}"
)

print(
    f"英国客户数："
    f"{int(英国记录['客户数']):,}"
)

print(
    f"英国销售额占比："
    f"{英国记录['销售额占比%']:.2f}%"
)



海外市场表 = 国家销售表[
    国家销售表["Country"]
    != "United Kingdom"
].copy()

海外前十市场 = (
    海外市场表
    .head(10)
    .copy()
)

print("\n===== 英国以外销售额最高的10个国家 =====")

print(
    海外前十市场[
        [
            "Country",
            "销售额",
            "订单数",
            "客户数",
            "平均客单价",
            "销售额占比%"
        ]
    ].to_string(index=False)
)


国家销售文件 = (
    处理后数据目录
    / "国家销售.csv"
)

国家销售表.to_csv(
    国家销售文件,
    index=False,
    encoding="utf-8-sig"
)




国家名称列表 = (
    海外前十市场["Country"]
    .astype(str)
    .tolist()
)

国家销售额列表 = (
    海外前十市场["销售额"]
    .astype(float)
    .tolist()
)

图形, 坐标轴 = plt.subplots(
    figsize=(10, 6)
)

坐标轴.barh(
    国家名称列表,
    国家销售额列表,
    color="#4E79A7"
)

坐标轴.set_title(
    "Top 10 International Markets"
)

坐标轴.set_xlabel(
    "Sales Amount (£)"
)

坐标轴.set_ylabel(
    "Country"
)

坐标轴.invert_yaxis()

坐标轴.grid(
    axis="x",
    alpha=0.25
)

图形.tight_layout()

海外市场图表文件 = (
    图表目录
    / "海外市场前十名.png"
)

图形.savefig(
    海外市场图表文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)



商品数据 = (
    销售数据
    .dropna(
        subset=["Description"]
    )
    .copy()
)

商品数据["Description"] = (
    商品数据["Description"]
    .astype("string")
    .str.strip()
)

print("\n===== 商品分析数据 =====")
print("商品分析明细：", len(商品数据))
print(
    "不重复商品编号：",
    商品数据["StockCode"].nunique()
)



商品销售表 = (
    商品数据
    .groupby(
        "StockCode",
        as_index=False
    )
    .agg(
        商品名称=("Description", "first"),
        销售额=("Sales", "sum"),
        销量=("Quantity", "sum"),
        订单数=("InvoiceNo", "nunique")
    )
)

商品销售表["平均销售单价"] = (
    商品销售表["销售额"]
    / 商品销售表["销量"]
)



服务费用代码 = [
    "POST",
    "DOT",
    "M",
    "BANK CHARGES",
    "C2",
    "PADS"
]

实际商品表 = 商品销售表[
    ~商品销售表["StockCode"].isin(
        服务费用代码
    )
].copy()


销售额前十商品 = (
    实际商品表
    .sort_values(
        "销售额",
        ascending=False
    )
    .head(10)
    .copy()
)

print("\n===== 销售额最高的10个商品 =====")

print(
    销售额前十商品[
        [
            "StockCode",
            "商品名称",
            "销售额",
            "销量",
            "订单数"
        ]
    ].to_string(index=False)
)


销量前十商品 = (
    实际商品表
    .sort_values(
        "销量",
        ascending=False
    )
    .head(10)
    .copy()
)

print("\n===== 销量最高的10个商品 =====")

print(
    销量前十商品[
        [
            "StockCode",
            "商品名称",
            "销量",
            "销售额",
            "订单数"
        ]
    ].to_string(index=False)
)

商品销售文件 = (
    处理后数据目录
    / "商品销售.csv"
)

商品销售表.to_csv(
    商品销售文件,
    index=False,
    encoding="utf-8-sig"
)

销售额商品名称 = (
    销售额前十商品["商品名称"]
    .astype(str)
    .tolist()
)

销售额商品数值 = (
    销售额前十商品["销售额"]
    .astype(float)
    .tolist()
)

销量商品名称 = (
    销量前十商品["商品名称"]
    .astype(str)
    .tolist()
)

销量商品数值 = (
    销量前十商品["销量"]
    .astype(float)
    .tolist()
)


图形, 坐标轴 = plt.subplots(
    1,
    2,
    figsize=(19, 7)
)


坐标轴[0].barh(
    销售额商品名称,
    销售额商品数值,
    color="#4E79A7"
)

坐标轴[0].set_title(
    "Top 10 Products by Sales"
)

坐标轴[0].set_xlabel(
    "Sales Amount (£)"
)

坐标轴[0].invert_yaxis()

坐标轴[0].grid(
    axis="x",
    alpha=0.25
)


坐标轴[1].barh(
    销量商品名称,
    销量商品数值,
    color="#59A14F"
)

坐标轴[1].set_title(
    "Top 10 Products by Quantity"
)

坐标轴[1].set_xlabel(
    "Quantity Sold"
)

坐标轴[1].invert_yaxis()

坐标轴[1].grid(
    axis="x",
    alpha=0.25
)


图形.tight_layout()

商品图表文件 = (
    图表目录
    / "商品销售前十名.png"
)

图形.savefig(
    商品图表文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)
print("\n===== 分析完成 =====")

print("国家销售数据：", 国家销售文件)
print("商品销售数据：", 商品销售文件)
print("海外市场图表：", 海外市场图表文件)
print("商品排名图表：", 商品图表文件)
