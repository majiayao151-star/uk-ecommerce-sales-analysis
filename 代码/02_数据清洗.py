from pathlib import Path

import pandas as pd


# 找到“电商销售分析”项目目录
项目目录 = Path(__file__).resolve().parents[1]

原始数据文件 = (
    项目目录
    / "数据"
    / "原始数据"
    / "Online Retail.xlsx"
)

处理后数据目录 = (
    项目目录
    / "数据"
    / "处理后数据"
)

# 如果处理后数据文件夹不存在，就自动创建
处理后数据目录.mkdir(
    parents=True,
    exist_ok=True
)




print("===== 读取原始数据 =====")

原始数据表 = pd.read_excel(
    原始数据文件,
    dtype={
        "InvoiceNo": "string",
        "StockCode": "string",
        "CustomerID": "string"
    }
)

原始数据表["InvoiceDate"] = pd.to_datetime(
    原始数据表["InvoiceDate"],
    errors="coerce"
)

print("原始数据行数：", len(原始数据表))





去重数据表 = (
    原始数据表
    .drop_duplicates()
    .copy()
)

删除重复数量 = (
    len(原始数据表)
    - len(去重数据表)
)

print("\n===== 删除重复记录 =====")
print("删除重复记录：", 删除重复数量)
print("去重后数据行数：", len(去重数据表))




取消订单标记 = (
    去重数据表["InvoiceNo"]
    .str.startswith(
        "C",
        na=False
    )
)

负数数量标记 = (
    去重数据表["Quantity"] < 0
)

print("\n===== 取消和负数数量检查 =====")
print("取消订单明细：", 取消订单标记.sum())
print("负数数量明细：", 负数数量标记.sum())




正常销售标记 = (
    (~取消订单标记)
    & (去重数据表["Quantity"] > 0)
    & (去重数据表["UnitPrice"] > 0)
    & (去重数据表["InvoiceDate"].notna())
)

正常销售数据 = (
    去重数据表
    .loc[正常销售标记]
    .copy()
)



正常销售数据["Sales"] = (
    正常销售数据["Quantity"]
    * 正常销售数据["UnitPrice"]
)

正常销售数据["YearMonth"] = (
    正常销售数据["InvoiceDate"]
    .dt.to_period("M")
    .astype("string")
)


客户分析数据 = (
    正常销售数据
    .dropna(
        subset=["CustomerID"]
    )
    .copy()
)

print("\n===== 正常销售与客户数据 =====")
print("正常销售明细：", len(正常销售数据))
print("客户分析明细：", len(客户分析数据))

print(
    "仅从客户分析排除的记录：",
    len(正常销售数据)
    - len(客户分析数据)
)



取消退货标记 = (
    取消订单标记
    | 负数数量标记
)

取消退货数据 = (
    去重数据表
    .loc[取消退货标记]
    .copy()
)

print("\n===== 取消退货数据 =====")
print(
    "取消或负数数量明细：",
    len(取消退货数据)
)

排除记录 = (
    去重数据表
    .loc[~正常销售标记]
    .copy()
)

print("\n===== 全部排除记录 =====")
print("排除记录数量：", len(排除记录))




print("\n===== 验证清洗结果 =====")

assert not 正常销售数据.duplicated().any()
assert (正常销售数据["Quantity"] > 0).all()
assert (正常销售数据["UnitPrice"] > 0).all()
assert (正常销售数据["Sales"] > 0).all()
assert 正常销售数据["InvoiceDate"].notna().all()

assert not (
    正常销售数据["InvoiceNo"]
    .str.startswith(
        "C",
        na=False
    )
    .any()
)

assert (
    客户分析数据["CustomerID"]
    .notna()
    .all()
)

print("所有清洗规则验证通过！")


正常销售文件 = (
    处理后数据目录
    / "正常销售.csv"
)

客户分析文件 = (
    处理后数据目录
    / "客户销售.csv"
)

取消退货文件 = (
    处理后数据目录
    / "取消退货.csv"
)

排除记录文件 = (
    处理后数据目录
    / "排除记录.csv"
)


正常销售数据.to_csv(
    正常销售文件,
    index=False,
    encoding="utf-8-sig"
)

客户分析数据.to_csv(
    客户分析文件,
    index=False,
    encoding="utf-8-sig"
)

取消退货数据.to_csv(
    取消退货文件,
    index=False,
    encoding="utf-8-sig"
)

排除记录.to_csv(
    排除记录文件,
    index=False,
    encoding="utf-8-sig"
)



print("\n===== 清洗完成 =====")
print("原始数据：", len(原始数据表))
print("删除重复：", 删除重复数量)
print("去重后数据：", len(去重数据表))
print("正常销售数据：", len(正常销售数据))
print("客户分析数据：", len(客户分析数据))
print("取消退货数据：", len(取消退货数据))
print("全部排除记录：", len(排除记录))

print("\n文件保存位置：")
print(处理后数据目录)
