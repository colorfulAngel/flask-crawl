import twstock
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
import matplotlib.pyplot as plt

def dataPreparation(name_attribute, target_stock, fetch_years):
    stock =  twstock.Stock(target_stock)
    
    # 計算起始日期：從今天往回 fetch_years 年
    today = datetime.today()
    # 將小數部分轉換成月數
    years_int = int(fetch_years)
    months_decimal = int(round((fetch_years - years_int) * 12, 0))
    start_date = today - relativedelta(years=years_int, months=months_decimal)
    start_year = start_date.year
    start_month = start_date.month

    print(f"抓取資料起始日期：{start_year}-{start_month}")

    # 取得資料：從計算出的起始年月開始抓取
    target_price = stock.fetch_from(start_year, start_month)

    #target_price = stock.fetch_from(2021, 10)
    print(target_price)

    # name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']
    df = pd.DataFrame(columns= name_attribute, data = target_price)
    print(df)
    return df, target_price
    

def resample_to_weekly(df):
    weekly_df = df.resample('W').agg({
        'Capacity': 'sum',
        'Turnover': 'sum',
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Change': 'sum',
        'Transcation': 'sum',
        'compdate': 'max',
    })

    return weekly_df

def calculate_five_line_spectrum(df):
    """
    輸入 DataFrame 必須包含：
    - 'Close'：收盤價
    - DataFrame 的索引為日期（datetime）
    此函數將計算：
    - 趨勢線：根據所有交易日以線性回歸計算 (y = a + b*x)
    - 母體標準差：整個資料區間，差異數 (Close - TrendLine) 的標準差
    - 95% 樂觀線、75% 樂觀線、75% 悲觀線、95% 悲觀線
    """
    # 複製 DataFrame 避免修改原始數據
    df = df.copy()

    # 產生交易日序號，從 1 起算（假設資料已按日期排序）
    df["TradingDay"] = np.arange(1, len(df)+1)

    # 線性回歸計算趨勢線：y = a + b*x，使用收盤價作為 y，TradingDay 作為 x
    X = sm.add_constant(df["TradingDay"])  # 增加截距項
    model = sm.OLS(df["Close"], X).fit()
    df["TrendLine"] = model.predict(X)

    # 計算差異數 = 收盤價 - 趨勢線
    df["Difference"] = df["Close"] - df["TrendLine"]

    # 計算整個資料區間的母體標準差 (使用 ddof=0)
    std_overall = np.std(df["Difference"], ddof=0)

    # 計算五線譜：
    df["95% Optimistic"] = df["TrendLine"] + 2 * std_overall
    df["75% Optimistic"] = df["TrendLine"] + 1 * std_overall
    df["75% Pessimistic"] = df["TrendLine"] - 1 * std_overall
    df["95% Pessimistic"] = df["TrendLine"] - 2 * std_overall

    # 回傳包含五線譜的 DataFrame
    return df, std_overall, model.params

def plotFiveLine(five_line_df, target_stock):
    
    # 設定圖表大小
    plt.figure(figsize=(12, 6))
    # 繪製股價五線譜
    plt.plot(five_line_df.index, five_line_df["Close"], color="blue", label="Close")
    plt.plot(five_line_df.index, five_line_df["TrendLine"], color="black", linestyle="dashed", label="TL")
    plt.plot(five_line_df.index, five_line_df["95% Optimistic"], color="red", linestyle="solid", label="+2 STDEV")
    plt.plot(five_line_df.index, five_line_df["75% Optimistic"], color="orange", linestyle="solid", label="+1 STDEV")
    plt.plot(five_line_df.index, five_line_df["75% Pessimistic"], color="green", linestyle="solid", label="-1 STDEV")
    plt.plot(five_line_df.index, five_line_df["95% Pessimistic"], color="darkgreen", linestyle="solid", label="-2 STDEV")

    # 標記最新數據點
    latest = five_line_df.iloc[-1]
    plt.scatter(latest.name, latest["Close"], color="blue", s=100, label=f"Price: {latest['Close']}")
    plt.scatter(latest.name, latest["TrendLine"], color="black", s=100, label=f"TL: {latest['TrendLine']}")
    plt.scatter(latest.name, latest["95% Optimistic"], color="red", s=100, label=f"+2 STDEV: {latest['95% Optimistic']}")
    plt.scatter(latest.name, latest["75% Optimistic"], color="orange", s=100, label=f"+1 STDEV: {latest['75% Optimistic']}")
    plt.scatter(latest.name, latest["75% Pessimistic"], color="green", s=100, label=f"-1 STDEV: {latest['75% Pessimistic']}")
    plt.scatter(latest.name, latest["95% Pessimistic"], color="darkgreen", s=100, label=f"-2 STDEV: {latest['95% Pessimistic']}")

    # 設定圖表標題與軸標籤
    plt.title(f"{target_stock} 樂活五線譜")
    plt.xlabel("日期")
    plt.ylabel("股價")

    # 加入圖例
    plt.legend(loc="upper left")

    # 顯示圖表
    # plt.show()
    plt.savefig('plotFiveLine.png')

def calculate_trend_bounds(weekly_df):
    # 過濾掉 Close 為 0 的資料
    df_trend = weekly_df[weekly_df['Capacity'] != 0].copy()

    # 計算 20 週移動平均的 Close (MA20)
    df_trend['MA20'] = df_trend['Close'].rolling(window=20, min_periods=1).mean()

    # 計算相關欄位
    df_trend['HL'] = df_trend['High'] - df_trend['Low']
    df_trend['H_plus_L_div2'] = (df_trend['High'] + df_trend['Low']) / 2
    df_trend['I_over_J'] = df_trend['HL'] / df_trend['H_plus_L_div2']
    df_trend['one_plus_2K'] = 1 + 2 * df_trend['I_over_J']
    df_trend['HX_L'] = df_trend['High'] * df_trend['one_plus_2K']
    df_trend['one_minus_2K'] = 2 - df_trend['one_plus_2K']  # 此處即 1-2K 的計算
    df_trend['L_N'] = df_trend['Low'] * df_trend['one_minus_2K']

    # 計算20週移動平均上界與下界 (若不足20筆則以 min_periods=1 計算)
    df_trend['upperbound'] = df_trend['HX_L'].rolling(window=20, min_periods=1).mean()
    df_trend['lowerbound'] = df_trend['L_N'].rolling(window=20, min_periods=1).mean()

    # 根據當週 Close 與上下界判斷突破信號
    def get_signal(row):
        if pd.notna(row['upperbound']) and row['Close'] > row['upperbound']:
            return "Breakout Up"
        elif pd.notna(row['lowerbound']) and row['Close'] < row['lowerbound']:
            return "Breakout Down"
        else:
            return "No Breakout"

    df_trend['Signal'] = df_trend.apply(get_signal, axis=1)
    return df_trend

def plotBigTrend(plot_df, target_stock):
    plt.figure(figsize=(12, 6))

    # 週線收盤價
    plt.plot(plot_df.index, plot_df['Close'], color="blue", label="Weekly Close")

    # 20MA
    plt.plot(plot_df.index, plot_df['MA20'], color="purple", linestyle="dashed", label="20MA")

    # 上下界
    plt.plot(plot_df.index, plot_df['upperbound'], color="red", label="Upper Bound")
    plt.plot(plot_df.index, plot_df['lowerbound'], color="green", label="Lower Bound")

    # 取最新一筆（可能為最近一週）
    if len(plot_df) > 0:
        latest = plot_df.iloc[-1]
        plt.scatter(latest.name, latest["Close"], color="blue", s=70,
                    label=f"Price: {latest['Close']}")
        plt.scatter(latest.name, latest["MA20"], color="purple", s=70,
                    label=f"MA20: {latest['MA20']}")
        plt.scatter(latest.name, latest["upperbound"], color="red", s=70,
                    label=f"Upper Bound: {latest['upperbound']}")
        plt.scatter(latest.name, latest["lowerbound"], color="green", s=70,
                    label=f"Lower Bound: {latest['lowerbound']}")

    plt.title(f"{target_stock} (20MA, Upper/Lower Bound)")
    plt.xlabel("日期")
    plt.ylabel("股價")
    plt.legend(loc="upper left")
    # plt.show()
    plt.savefig('plotBigTrend.png')



