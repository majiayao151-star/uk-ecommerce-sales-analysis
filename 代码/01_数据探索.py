from pathlib import Path

import pandas as pd


# 当前程序位于“代码”文件夹
# parents[1]返回上一层“电商销售分析”
项目目录 = Path(__file__).resolve().parents[1]

数据目录 = 项目目录 / "数据"
原始数据目录 = 数据目录 / "原始数据"

数据文件 = (
    原始数据目录
    / "Online Retail.xlsx"
)


print("===== 文件位置检查 =====")
print("项目目录：", 项目目录)
print("数据目录存在：", 数据目录.exists())
print("原始数据目录存在：", 原始数据目录.exists())
print("数据文件：", 数据文件)
print("文件是否存在：", 数据文件.exists())


# 如果文件不存在，列出实际文件名以便检查
if not 数据文件.exists():
    print("\n没有找到指定的Excel文件。")

    if 原始数据目录.exists():
        print("原始数据文件夹中的文件：")

        for 文件 in 原始数据目录.iterdir():
            print("  ", 文件.name)

    raise FileNotFoundError(
        f"没有找到数据文件：{数据文件}"
    )


# 读取Excel数据
数据表 = pd.read_excel(
    数据文件,
    dtype={
        "InvoiceNo": "string",
        "StockCode": "string",
        "CustomerID": "string"
    }
)


print("\n===== 数据读取成功 =====")
print("数据行数：", len(数据表))
print("字段数量：", 数据表.shape[1])

print("\n===== 字段名称 =====")
print(数据表.columns.tolist())

print("\n===== 前5行数据 =====")
print(数据表.head())


print("\n===== 1. 字段类型检查 =====")
print(数据表.dtypes)


数据表["InvoiceDate"] = pd.to_datetime(
    数据表["InvoiceDate"],
    errors="coerce"
)

无效日期数量 = (
    数据表["InvoiceDate"]
    .isna()
    .sum()
)

print("\n===== 2. 日期检查 =====")
print(
    "最早交易时间：",
    数据表["InvoiceDate"].min()
)
print(
    "最晚交易时间：",
    数据表["InvoiceDate"].max()
)
print("无效日期数量：", 无效日期数量)



缺失数量 = 数据表.isna().sum()

缺失比例 = (
    数据表.isna().mean()
    * 100
).round(2)

缺失汇总 = pd.DataFrame({
    "缺失数量": 缺失数量,
    "缺失比例%": 缺失比例
})

print("\n===== 3. 缺失值检查 =====")
print(缺失汇总)





重复记录数量 = (
    数据表.duplicated()
    .sum()
)

重复记录比例 = (
    重复记录数量
    / len(数据表)
    * 100
)

print("\n===== 4. 重复记录检查 =====")
print("完全重复记录：", 重复记录数量)
print(
    "重复记录比例：",
    round(重复记录比例, 2),
    "%"
)


取消标记 = (
    数据表["InvoiceNo"]
    .str.startswith(
        "C",
        na=False
    )
)

取消明细数量 = 取消标记.sum()

取消订单数量 = (
    数据表.loc[
        取消标记,
        "InvoiceNo"
    ]
    .nunique()
)

print("\n===== 5. 取消订单检查 =====")
print("取消订单明细行数：", 取消明细数量)
print("取消订单数量：", 取消订单数量)







负数数量记录 = (
    数据表["Quantity"] < 0
).sum()

零数量记录 = (
    数据表["Quantity"] == 0
).sum()

print("\n===== 6. 商品数量检查 =====")
print("数量小于0：", 负数数量记录)
print("数量等于0：", 零数量记录)



负数价格记录 = (
    数据表["UnitPrice"] < 0
).sum()

零价格记录 = (
    数据表["UnitPrice"] == 0
).sum()



订单数量 = (
    数据表["InvoiceNo"]
    .nunique()
)

客户数量 = (
    数据表["CustomerID"]
    .nunique()
)

商品数量 = (
    数据表["StockCode"]
    .nunique()
)

国家数量 = (
    数据表["Country"]
    .nunique()
)

print("\n===== 8. 基础数量检查 =====")
print("不重复订单数量：", 订单数量)
print("可识别客户数量：", 客户数量)
print("不重复商品数量：", 商品数量)
print("国家数量：", 国家数量)
print("\n===== 7. 商品价格检查 =====")
print("价格小于0：", 负数价格记录)
print("价格等于0：", 零价格记录)


示例订单号 = (
    数据表.iloc[0]["InvoiceNo"]
)

示例订单 = 数据表[
    数据表["InvoiceNo"]
    == 示例订单号
]

print("\n===== 9. 订单结构示例 =====")
print("示例订单号：", 示例订单号)
print("这个订单的明细行数：", len(示例订单))

print(
    示例订单[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "UnitPrice"
        ]
    ]
)
