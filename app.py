import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

def busy_hours(hour_df) :
    busy_hours_df = hour_df.groupby('hr')['cnt'].sum()
    busy_hours_df = busy_hours_df.reset_index()
    busy = pd.DataFrame(busy_hours_df)
    busy.sort_values(by='cnt', ascending=False, inplace=True)
    busy['hr'] = busy['hr'].apply(lambda x: f"{x:02d}:00")
    return busy

def daily_rent(day_df) :
    daily_renter_df = day_df[['dteday','casual', 'registered', 'cnt']]
    daily_renter_df.rename(columns={
            "dteday": "date",
            "cnt": "rent_count"
        }, inplace=True)
    return daily_renter_df

def season_day_rent(day_df) :
    def season_string(day_df) :
        seasons = {
            1 : "Spring",
            2 : "Summer",
            3 : "Fall",
            4 : "Winter"
        }
        return seasons[day_df['season']]
    def day_string(day_df) :
        days = {
            1 : "Monday",
            2 : "Tuesday",
            3 : "Wednesday",
            4 : "Thursday",
            5 : "Friday",
            6 : "Saturday",
            0 : "Sunday"
        }
        return days[day_df['weekday']]
    day_df["weekday"] = day_df.apply(day_string,axis=1)
    day_df["season"] = day_df.apply(season_string,axis=1)
    
    #urutkan season
    season = pd.DataFrame(day_df.groupby(by="season").cnt.sum())
    season = season.reset_index()
    season_order = ['Spring','Summer','Fall','Winter']
    season['season'] = pd.Categorical(season['season'], categories=season_order, ordered=True)
    season = season.sort_values('season')
    
    #urutkan day
    week_day = pd.DataFrame(day_df.groupby(by="weekday").cnt.sum())
    week_day = week_day.reset_index()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_day['weekday'] = pd.Categorical(week_day['weekday'], categories=day_order, ordered=True)
    week_day = week_day.sort_values('weekday')
    return season, week_day
        

day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")
datetime_column = "dteday"

hour_df[datetime_column] = pd.to_datetime(hour_df[datetime_column])
day_df[datetime_column] = pd.to_datetime(day_df[datetime_column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Mengambil start_date & end_date dari date_input
start_date, end_date = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
hours_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

daily_rent_df = daily_rent(main_df)
season_rent_df, day_rent_df = season_day_rent(main_df)
busy_hours_df = busy_hours(hours_df)

st.header('Bycicle Rent Demographic 🚲')

st.subheader('Rent Statistics')
 
total_orders = daily_rent_df.rent_count.sum()
st.metric("Total Rent", value=total_orders)
    
plt.figure(figsize=(20, 10)) 
plt.plot(
    daily_rent_df['date'],
    daily_rent_df["rent_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
) 
plt.tick_params(axis='y', labelsize=20)
plt.tick_params(axis='x', labelsize=18)
st.pyplot(plt)

col1, col2, col3 = st.columns([1,1,2])

with col1 :
    total_casual = daily_rent_df.casual.sum()
    st.metric("Total Casual Rent", value=total_casual)

with col2 :
    total_registered = daily_rent_df.registered.sum()
    st.metric("Total Registered Rent", value=total_registered)
    
with col3 :
    busy_hr = busy_hours_df.iloc[0]['hr']
    st.metric("Busiest Hour", value=busy_hr)    

col1, col2, = st.columns(2)

with col1 :
    plt.figure(figsize=(20, 11)) 
    plt.bar(
        ('Casual', 'Registered'), 
        (daily_rent_df['casual'].sum(), daily_rent_df['registered'].sum()), 
        color='skyblue')
    plt.tick_params(axis='y', labelsize=20)
    plt.tick_params(axis='x', labelsize=18)
    plt.gca().get_yaxis().get_major_formatter().set_scientific(False)
    plt.ylabel('Count')
    st.pyplot(plt)

with col2 :
    plt.figure(figsize=(35, 20))
    sns.barplot(x="cnt", y="hr", data=busy_hours_df.head(5))
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='y', labelsize=35)
    plt.tick_params(axis='x', labelsize=30)
    st.pyplot(plt)

st.subheader('Bycicle Rent Statistics Based on Day and Season')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
sns.barplot(x="season", y="cnt", data=season_rent_df, ax=ax[0])
ax[0].ticklabel_format(style='plain', axis='y')
ax[0].set_ylabel('Count')
ax[0].set_xlabel('')
ax[0].set_title("Bycicle Rent Statistics Based on Season", loc="center", fontsize=15)

sns.barplot(x="weekday", y="cnt", data=day_rent_df, ax=ax[1])
ax[1].ticklabel_format(style='plain', axis='y')
ax[1].set_ylabel('Count')
ax[1].set_xlabel('')
ax[1].set_title("Bycicle Rent Statistics Based on Day", loc="center", fontsize=15)
st.pyplot(fig)

st.subheader('Temperature Effect on Bycicle Rent')
plt.figure(figsize=(16, 8))
plt.scatter(
    main_df["temp"]*41, #temperatur dalam data ternormalisasi dengan nilai max 41
    main_df["cnt"],
    marker='o', 
    color="#90CAF9"
)
plt.tick_params(axis='y', labelsize=20)
plt.tick_params(axis='x', labelsize=15)
plt.xlabel('Temperature (°C)', fontsize=15)
st.pyplot(plt)