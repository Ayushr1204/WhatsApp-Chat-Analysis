import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="WhatsApp Chat Analysis",
    layout="wide",
)


st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis for ", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Total Links Shared")
            st.title(num_links)

        if selected_user == "Overall":
            st.title("Most active users")
            x, new_df = helper.most_active_users(df)
            x.drop(labels='group_notification', axis=0, inplace=True, errors='ignore')
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='green')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)


        # WordCloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        st.title("Most common words")
        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()

        ax.barh(most_common_df[0], most_common_df[1])
        st.pyplot(fig)

        # emoji analysis
        import matplotlib.pyplot as plt

        st.title("Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        # Rename columns in place
        emoji_df.rename(columns={0: 'Emoji', 1: 'Count'}, inplace=True)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            # Bigger figure
            fig, ax = plt.subplots(figsize=(8, 8))

            # Take top 5 emojis
            top_emojis = emoji_df.head(5)

            # Use Segoe UI Emoji font (Windows) or Apple Color Emoji (macOS)
            plt.rcParams['font.family'] = 'Segoe UI Emoji'

            ax.pie(
                top_emojis['Count'],
                labels=top_emojis['Emoji'],
                autopct="%0.1f%%",
                startangle=90,
                textprops={'fontsize': 18, 'weight': 'bold'}  # Bigger & bolder labels
            )
            ax.axis("equal")
            st.pyplot(fig)

        # monthly timeline
        st.title("Monthly timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # daily timeline
        st.title("Daily timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='blue')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Busiest Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.header("Busiest Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        user_heatmap = helper.activity_heatmap(selected_user, df)

        user_heatmap = user_heatmap.astype(int)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax = sns.heatmap(
            user_heatmap,
            cmap="YlGnBu",
            annot=True,
            fmt="d",
            linewidths=0.3,
            cbar_kws={'label': 'Message Count'}
        )

        ax.set_xlabel("Hour Range", fontsize=12)
        ax.set_ylabel("Day", fontsize=12)
        ax.set_title("Weekly Activity Heatmap", fontsize=14)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        st.pyplot(fig)

