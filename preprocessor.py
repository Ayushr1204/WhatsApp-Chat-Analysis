import re
import pandas as pd

def preprocess(data):
    # WhatsApp formats can vary -> handle both DD/MM/YYYY and MM/DD/YYYY
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    if not dates:
        print("⚠️ No matches found. Check your chat export format!")
        return pd.DataFrame(columns=['date','user','message'])

    # build DataFrame
    df = pd.DataFrame({'message_date': [d[0] + " " + d[1] for d in dates], 'user_message': messages[::3]})

    # try different datetime formats
    for fmt in ('%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M', '%d/%m/%Y %I:%M %p', '%m/%d/%Y %I:%M %p'):
        try:
            df['date'] = pd.to_datetime(df['message_date'], format=fmt)
            break
        except ValueError:
            continue

    # Separate users & messages
    users, messages = [], []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message','message_date'], inplace=True)

    # Add time-based features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create hour ranges
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour+1}")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df
