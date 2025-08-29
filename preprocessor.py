import re
import pandas as pd

def preprocess(data):
    # Regex for your format: "23/02/24, 4:52 pm - ..."
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s?[apAP][mM])\s-\s'
    
    # Split messages
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    if not dates:
        print("⚠️ No matches found! Check export format.")
        return pd.DataFrame(columns=['date','user','message'])

    # Build DataFrame
    df = pd.DataFrame({
        'message_date': [d[0] + " " + d[1] for d in dates],
        'user_message': messages[2::3]   # every 3rd item is actual message text
    })

    # Convert to datetime (your format: dd/mm/yy h:mm am/pm)
    df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y %I:%M %p', errors='coerce')

    # Separate user and message
    users, msgs = [], []
    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg)
        if len(entry) >= 3:
            users.append(entry[1])
            msgs.append(entry[2])
        else:
            users.append("group_notification")
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message','message_date'], inplace=True)

    # Extract more datetime features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period (hour ranges)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df
