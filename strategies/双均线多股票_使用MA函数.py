# coding: utf-8  # 源文件编码
# 策略说明：
# - 策略名称：双均线多股票（使用 MyTT.MA）
# - 功能：对股票池内每只股票，比较当日 MA5 与 MA20；MA5>MA20 买入，MA5<MA20 卖出
# - 指标来源：使用 MyTT 库的 MA 函数（对收盘价序列计算均线）
# - 与使用 MyTT.MA 的版本区别：khMA 中内置了行情获取 + 移动平均，更加方便，MyTT.MA 需要在策略文档中先拉取历史行情再计算
from khQuantImport import *  # 统一导入工具与指标

def init(stocks=None, data=None):  # 策略初始化（无需特殊处理）
    """本策略不需初始化"""
    pass  # 占位


def khHandlebar(data: Dict) -> List[Dict]:  # 主策略函数
    """多股票双均线（MyTT.MA）策略：MA5 上穿 MA20 买入，反向卖出"""
    signals = []  # 信号列表
    stock_list = khGet(data, "stocks")  # 股票池
    dn = khGet(data, "date_num")  # 当前日期(数值格式)

    for sc in stock_list:  # 遍历股票
        hist = khHistory(sc, ["close"], 60, "1d", dn, fq="pre", force_download=False)  # 拉取60日收盘价
        
        # 数据有效性检查：1. 字典中存在 2. DataFrame 非空
        if sc not in hist or hist[sc] is None or hist[sc].empty:
            continue  # 无数据时跳过该股票
        
        df = hist[sc]

        # 新增：检查是否真的有 'close' 这一列
        if "close" not in df.columns:
            # 这里可以根据需要加一行日志（如果策略环境允许打印 / logging）
            # print(f"警告: {sc} 的历史数据中无 'close' 列，实际列为: {list(df.columns)}")
            continue

        closes = df["close"].values  # 收盘序列
        
        # 检查数据量是否足够计算MA20（至少需要20个数据点）
        if len(closes) < 20:
            continue  # 数据不足时跳过该股票
        
        ma5_result = MA(closes, 5)  # 计算MA5
        ma20_result = MA(closes, 20)  # 计算MA20
        
        # 检查MA计算结果是否有效（去除NaN值后是否有数据）
        if len(ma5_result) == 0 or len(ma20_result) == 0:
            continue  # MA计算结果为空时跳过
        
        # 由于MA函数在前期会返回NaN，需要检查最后一个值是否为有效数字
        import numpy as np
        if np.isnan(ma5_result[-1]) or np.isnan(ma20_result[-1]):
            continue  # 最新值为NaN时跳过
        
        ma5_now = float(ma5_result[-1])  # 当日MA5
        ma20_now = float(ma20_result[-1])  # 当日MA20

        price = khPrice(data, sc, "open")  # 当日开盘价
        has_pos = khHas(data, sc)  # 是否持仓

        if ma5_now > ma20_now and not has_pos:  # 金叉且无持仓→买入
            signals.extend(generate_signal(data, sc, price, 0.5, "buy", f"{sc[:6]} 金叉买入"))  # 0.5仓
        elif ma5_now < ma20_now and has_pos:  # 死叉且有持仓→卖出
            signals.extend(generate_signal(data, sc, price, 1.0, "sell", f"{sc[:6]} 死叉卖出"))  # 全部卖出

    return signals  # 返回信号

