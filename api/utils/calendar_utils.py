from datetime import datetime

def divide_datetime(datetime_series):
    day_list = []
    time_list = []
    for date_time in datetime_series:
        if date_time is None:
            day_list.append(None)
            time_list.append(None)
            continue
        day = str(date_time.month).zfill(2) + "/" + str(date_time.day).zfill(2) + "/" + str(date_time.year)
        time = str(date_time.hour).zfill(2) + ":" + str(date_time.minute).zfill(2)
        day_list.append(day)
        time_list.append(time)
    return day_list, time_list

def df_to_ics(df):
    if df is None:
        return None
    if not df.empty:
        df["Start Date"], df["Start Time"] = divide_datetime(df['StartDateTime'])
        df["End Date"], df["End Time"] = divide_datetime(df['EndDateTime'])

        # enter dummy columns for ics formatting
        df["All Day Event"] = ["False"] * len(df)
        df["Private"] = ["False"] * len(df)
        df = df[['title','Start Date','End Date', 'Start Time', 'End Time', 'All Day Event', 'memo', 'Private']]
        df.columns = ['Subject','Start Date','End Date', 'Start Time', 'End Time', 'All Day Event', 'Description', 'Private']
    return df