import api

def getBigTrend(target_stock, fetch_years):
    status_code, df = api.getBigTrend(target_stock, fetch_years)
    # api.getBigTrend(target_stock, fetch_years)
    print(f"status_code:{status_code}, fetch_years:{fetch_years}")
    df.to_json('df.json', orient='records', lines=True)

if __name__ == '__main__':
    getBigTrend("0050", 3.5)
    print('End')