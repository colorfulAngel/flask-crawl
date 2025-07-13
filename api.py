import service as svc
import pandas as pd
import time

name_attribute = ['Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change', 'Transcation']

def getBigTrendTest(target_stock, fetch_years):
    print(f'test, target_stock:{target_stock}, fetch_years:{fetch_years}')
    return "Success", ""

def getRaw(target_stock, fetch_years):
    start_time = time.time()

    # 股票爬蟲與資料準備==================================
    df, target_price = svc.dataPreparation(name_attribute, target_stock, fetch_years)
    # df2 = pd.DataFrame( columns= name_attribute, data = target_price)
    df['compdate']=df['Date']
    df.set_index('Date', inplace=True)
    weekly_df = svc.resample_to_weekly(df)

    elapsed_time = time.time() - start_time
    print(f"[getRaw] Execution time: {elapsed_time:.4f} seconds")
    
    return df, weekly_df

def getFive(target_stock, fetch_years):
    try:
        start_time = time.time()

        df2, weekly_df=getRaw(target_stock, fetch_years)
        # 股價五線譜計算：根據整個母體資料計算趨勢線與標準差==================================
        # 將股價五線譜計算整合進主程式：以原始爬取的資料 df2（以 Date 為索引）
        five_line_df, std_val, params = svc.calculate_five_line_spectrum(df2)
        # print("股價五線譜計算結果:")
        # print(five_line_df[["Close", "TrendLine", "Difference", "95% Optimistic", "75% Optimistic", "75% Pessimistic", "95% Pessimistic"]])

        # 儲存股價五線譜計算結果至 CSV，供後續分析使用
        # filename_five = f'{target_stock}_five_line_spectrum.csv'
        # five_line_df.to_csv(filename_five)

        # 繪製股價五線譜
        # svc.plotFiveLine(five_line_df, target_stock)
        elapsed_time = time.time() - start_time
        print(f"[getFive] Execution time: {elapsed_time:.4f} seconds")

        return 200, five_line_df
    except Exception as e:
        # print(str(e))
        return 500, str(e)
    

def getBigTrend(target_stock, fetch_years):
    try:
        start_time = time.time()

        # 股票爬蟲與資料準備==================================
        # 週線重採樣 (原有功能)==================================
       
        df2, weekly_df=getRaw(target_stock, fetch_years)
        # filename = f'{target_stock}.csv'
        # df2.to_csv(filename)
        
        # 大趨勢運算(BigTrend)：計算上界與下界==================================
        trend_df = svc.calculate_trend_bounds(weekly_df)
        # print("大趨勢運算結果:")
        # print(trend_df[['Close', 'MA20', 'upperbound', 'lowerbound', 'Signal']])

        # filename_trend = f'{target_stock}_trend_bounds.csv'
        # trend_df.to_csv(filename_trend)

        # 繪圖前把 Close=0 的那週資料"整筆"移除
        # plot_df = trend_df.copy()

        # 刪除 Close=0 的該筆資料（包含該日期）
        # plot_df = plot_df[plot_df['Capacity'] != 0]

        # 繪製大趨勢圖表 (週線收盤、MA20、Upper、Lower)
        # svc.plotBigTrend(plot_df, target_stock)
        
        elapsed_time = time.time() - start_time
        print(f"[getBigTrend] Execution time: {elapsed_time:.4f} seconds")
        
        # return 200, "Success"
        return 200, trend_df
    except Exception as e:
        # print(str(e))
        return 500, str(e)
