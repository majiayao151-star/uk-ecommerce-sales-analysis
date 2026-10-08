import os
from pathlib import Path


项目目录 = Path(__file__).resolve().parents[1]

客户汇总文件 = (
    项目目录
    / "数据"
    / "处理后数据"
    / "客户汇总.csv"
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
print("===== 读取客户汇总数据 =====")

客户汇总表 = pd.read_csv(
    客户汇总文件,
    dtype={
        "CustomerID": "string"
    }
)

客户汇总表["首次购买时间"] = pd.to_datetime(
    客户汇总表["首次购买时间"],
    errors="coerce"
)

客户汇总表["最后购买时间"] = pd.to_datetime(
    客户汇总表["最后购买时间"],
    errors="coerce"
)

print("客户数量：", len(客户汇总表))

print(
    "最后购买日期范围：",
    客户汇总表["最后购买时间"].min(),
    "至",
    客户汇总表["最后购买时间"].max()
)

数据最后交易日 = (
    客户汇总表["最后购买时间"]
    .max()
)

分析日期 = (
    数据最后交易日
    + pd.Timedelta(days=1)
)

print("\n===== RFM分析日期 =====")
print("数据最后交易日：", 数据最后交易日)
print("RFM分析日期：", 分析日期)



客户汇总表["R_最近购买间隔"] = (
    分析日期
    - 客户汇总表["最后购买时间"]
).dt.days

客户汇总表["F_购买频次"] = (
    客户汇总表["购买次数"]
)

客户汇总表["M_消费金额"] = (
    客户汇总表["累计消费金额"]
)

print("\n===== RFM指标示例 =====")

print(
    客户汇总表[
        [
            "CustomerID",
            "R_最近购买间隔",
            "F_购买频次",
            "M_消费金额"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

R百分位 = (
    客户汇总表["R_最近购买间隔"]
    .rank(
        pct=True,
        ascending=False
    )
)

F百分位 = (
    客户汇总表["F_购买频次"]
    .rank(
        pct=True,
        ascending=True
    )
)

M百分位 = (
    客户汇总表["M_消费金额"]
    .rank(
        pct=True,
        ascending=True
    )
)



客户汇总表["R评分"] = pd.cut(
    R百分位,
    bins=[
        0,
        0.25,
        0.50,
        0.75,
        1
    ],
    labels=[
        1,
        2,
        3,
        4
    ],
    include_lowest=True
).astype(int)

客户汇总表["F评分"] = pd.cut(
    F百分位,
    bins=[
        0,
        0.25,
        0.50,
        0.75,
        1
    ],
    labels=[
        1,
        2,
        3,
        4
    ],
    include_lowest=True
).astype(int)

客户汇总表["M评分"] = pd.cut(
    M百分位,
    bins=[
        0,
        0.25,
        0.50,
        0.75,
        1
    ],
    labels=[
        1,
        2,
        3,
        4
    ],
    include_lowest=True
).astype(int)


客户汇总表["RFM总分"] = (
    客户汇总表["R评分"]
    + 客户汇总表["F评分"]
    + 客户汇总表["M评分"]
)

客户汇总表["RFM组合"] = (
    客户汇总表["R评分"].astype(str)
    + 客户汇总表["F评分"].astype(str)
    + 客户汇总表["M评分"].astype(str)
)

print("\n===== RFM评分示例 =====")

print(
    客户汇总表[
        [
            "CustomerID",
            "R_最近购买间隔",
            "F_购买频次",
            "M_消费金额",
            "R评分",
            "F评分",
            "M评分",
            "RFM总分",
            "RFM组合"
        ]
    ]
    .head(10)
    .to_string(index=False)
)



def 判断客户分层(客户记录):
    R分 = 客户记录["R评分"]
    F分 = 客户记录["F评分"]
    M分 = 客户记录["M评分"]

    if R分 >= 3 and F分 >= 3 and M分 >= 3:
        return "冠军客户"

    elif R分 <= 2 and M分 >= 3:
        return "高价值流失风险"

    elif F分 >= 3:
        return "忠诚客户"

    elif R分 >= 3 and F分 <= 2:
        return "近期客户"

    else:
        return "需要关注"


客户汇总表["客户分层"] = (
    客户汇总表.apply(
        判断客户分层,
        axis=1
    )
)



客户分层汇总表 = (
    客户汇总表
    .groupby(
        "客户分层",
        as_index=False
    )
    .agg(
        客户数量=("CustomerID", "count"),
        总销售额=("M_消费金额", "sum"),
        平均消费金额=("M_消费金额", "mean"),
        平均购买次数=("F_购买频次", "mean"),
        平均最近购买间隔=(
            "R_最近购买间隔",
            "mean"
        )
    )
)

客户分层汇总表["客户占比%"] = (
    客户分层汇总表["客户数量"]
    / 客户分层汇总表["客户数量"].sum()
    * 100
)

客户分层汇总表["销售额占比%"] = (
    客户分层汇总表["总销售额"]
    / 客户分层汇总表["总销售额"].sum()
    * 100
)

客户分层汇总表 = (
    客户分层汇总表
    .sort_values(
        "总销售额",
        ascending=False
    )
    .reset_index(drop=True)
)


print("\n===== RFM客户分层结果 =====")

print(
    客户分层汇总表.to_string(
        index=False
    )
)
# =========================
# 保存RFM分析结果
# =========================

RFM客户明细文件 = (
    处理后数据目录
    / "RFM客户明细.csv"
)

RFM分层汇总文件 = (
    处理后数据目录
    / "RFM客户分层汇总.csv"
)


客户汇总表.to_csv(
    RFM客户明细文件,
    index=False,
    encoding="utf-8-sig"
)

客户分层汇总表.to_csv(
    RFM分层汇总文件,
    index=False,
    encoding="utf-8-sig"
)

print("\n===== RFM数据保存完成 =====")
print("客户明细行数：", len(客户汇总表))
print("客户分层数量：", len(客户分层汇总表))
英文分层名称 = {
    "冠军客户": "Champions",
    "高价值流失风险": "At Risk High Value",
    "忠诚客户": "Loyal Customers",
    "近期客户": "Recent Customers",
    "需要关注": "Need Attention"
}

图表分层名称 = (
    客户分层汇总表["客户分层"]
    .map(英文分层名称)
    .astype(str)
    .tolist()
)

图表客户数量 = (
    客户分层汇总表["客户数量"]
    .astype(int)
    .tolist()
)

图表销售额占比 = (
    客户分层汇总表["销售额占比%"]
    .astype(float)
    .tolist()
)


图形, 坐标轴 = plt.subplots(
    1,
    2,
    figsize=(16, 6)
)


坐标轴[0].barh(
    图表分层名称,
    图表客户数量,
    color="#4E79A7"
)

坐标轴[0].set_title(
    "Customers by RFM Segment"
)

坐标轴[0].set_xlabel(
    "Number of Customers"
)

坐标轴[0].invert_yaxis()

坐标轴[0].grid(
    axis="x",
    alpha=0.25
)


坐标轴[1].barh(
    图表分层名称,
    图表销售额占比,
    color="#F28E2B"
)

坐标轴[1].set_title(
    "Sales Share by RFM Segment"
)

坐标轴[1].set_xlabel(
    "Sales Share (%)"
)

坐标轴[1].invert_yaxis()

坐标轴[1].grid(
    axis="x",
    alpha=0.25
)


图形.tight_layout()

RFM图表文件 = (
    图表目录
    / "RFM客户分层.png"
)

图形.savefig(
    RFM图表文件,
    dpi=300,
    bbox_inches="tight"
)

plt.close(图形)


print("\n===== RFM分析完成 =====")

print("RFM客户明细：", RFM客户明细文件)
print("RFM分层汇总：", RFM分层汇总文件)
print("RFM分层图表：", RFM图表文件)
