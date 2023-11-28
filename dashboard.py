import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set up the layout
sns.set(style="whitegrid")

# Fungsi untuk memuat dan menggabungkan data
@st.cache(allow_output_mutation=True)
def load_data():
    files = [
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Aotizhongxin_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Changping_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Dingling_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Dongsi_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Guanyuan_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Gucheng_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Huairou_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Nongzhanguan_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Shunyi_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Tiantan_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Wanliu_20130301-20170228.csv",
        "https://raw.githubusercontent.com/alaik10/Dashboard/main/PRSA_Data_Wanshouxigong_20130301-20170228.csv"
    ]

 datasets = []
    for file in files:
        df = pd.read_csv(file)
        # Standardize column names here if necessary
        # For example, if some files have 'date' instead of 'datetime'
        if 'date' in df.columns:
            df.rename(columns={'date': 'datetime'}, inplace=True)
        datasets.append(df)
    
    merged_data = pd.concat(datasets, ignore_index=True)
    return merged_data

data = load_data()

# Now check if 'datetime' column exists
if 'datetime' in data.columns:
    data['datetime'] = pd.to_datetime(data['datetime'])
else:
    st.error("Column 'datetime' not found in the dataset.")

last_date = data['datetime'].max()
# Calculate the start date of the last month
start_last_month = last_date - pd.DateOffset(months=1)

# Filter 
last_month_data = data[data['datetime'] >= start_last_month]


# Group by station and date to see the daily trend
daily_pm25_last_month = last_month_data.groupby(['station', last_month_data['datetime'].dt.date])['PM2.5'].mean().reset_index()

# Pivot the data for easier plotting
pivot_daily_pm25 = daily_pm25_last_month.pivot(index='datetime', columns='station', values='PM2.5')

# Calculate mean PM2.5 for the last month for each station
mean_pm25_last_month = last_month_data.groupby('station')['PM2.5'].mean().sort_values()

# 3. Frequency of Air Quality Decline at Each Station
# We can calculate the number of days each station exceeded a certain PM2.5 threshold
threshold = 100  # Example threshold for poor air quality
days_exceeding_threshold = last_month_data[last_month_data['PM2.5'] > threshold].groupby('station').size()


# Judul Dashboard
st.title('Dashboard Analisis Kualitas Udara 🌥️💨🌦️')

# Visualisasi 1: Grafik batang rata-rata tingkat PM2.5 dan PM10 per stasiun
st.subheader('Rata-rata Tingkat kualitas udara buruk dan polusi setiap daerah')
st.text('Grafik batang ini menunjukkan rata-rata tingkat PM2.5 dan PM10 untuk setiap stasiun. '
        'PM2.5 dan PM10 adalah partikel berukuran kecil dalam udara yang bisa berbahaya bagi kesehatan.')
avg_pollution = data.groupby('station')[['PM2.5', 'PM10']].mean().reset_index()
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
sns.barplot(x='PM2.5', y='station', data=avg_pollution, ax=ax[0])
ax[0].set_title('Rata-rata PM2.5 per Stasiun')
sns.barplot(x='PM10', y='station', data=avg_pollution, ax=ax[1])
ax[1].set_title('Rata-rata PM10 per Stasiun')
st.pyplot(fig)


# Visualisasi 2: Grafik garis rata-rata tingkat PM2.5 harian menurut stasiun
# Plotting
st.subheader('Rata-rata Tingkat kualitas udara buruk Harian setiap daerah')
st.text('Grafik garis ini menampilkan tren rata-rata tingkat PM2.5 setiap hari di berbagai stasiun '
        'selama bulan terakhir. Ini membantu mengidentifikasi pola dan perubahan kualitas udara seiring waktu.')
fig, ax = plt.subplots(figsize=(15, 8))
sns.lineplot(data=pivot_daily_pm25, ax=ax, dashes=False)
ax.set_title('Rata-rata Tingkat PM2.5 Harian menurut Stasiun (Bulan Lalu)')
ax.set_ylabel('Mean PM2.5')
ax.set_xlabel('Date')
plt.xticks(rotation=45)
ax.legend(title='Station', loc='upper right')
st.pyplot(fig)


# Visualisasi 3: Grafik batang rata-rata tingkat PM2.5 menurut stasiun
st.subheader('Rata-rata Tingkat penurunan kualitas udara menurut daerah')
st.text('Grafik batang ini menggambarkan rata-rata tingkat PM2.5 di setiap stasiun selama bulan terakhir. '
        'Ini memberikan pandangan umum tentang stasiun mana yang memiliki kualitas udara lebih baik atau lebih buruk.')
fig, ax = plt.subplots(figsize=(12, 6))
mean_pm25_last_month.plot(kind='bar', color='red', ax=ax)
ax.set_title('Rata-rata Tingkat PM2.5 menurut Stasiun (Bulan Lalu)')
ax.set_ylabel('Average PM2.5')
ax.set_xlabel('Station')
plt.xticks(rotation=45)
st.pyplot(fig)

# Visualisasi 4: Grafik batang jumlah hari yang melebihi ambang batas PM2.5
st.subheader('Jumlah Hari yang Melebihi Ambang Batas standar kualitas udara buruk Berdasarkan daerah')
st.text('Grafik batang ini menampilkan jumlah hari di mana tingkat PM2.5 di setiap stasiun melebihi ambang batas tertentu. '
        'Ini penting untuk menilai frekuensi peristiwa kualitas udara buruk di berbagai lokasi.')
fig, ax = plt.subplots(figsize=(12, 6))
days_exceeding_threshold.plot(kind='bar', color='blue', ax=ax)
ax.set_title('Jumlah Hari yang Melebihi Ambang Batas PM2.5 Berdasarkan Stasiun (Bulan Lalu)')
ax.set_ylabel('Number of Days')
ax.set_xlabel('Station')
plt.xticks(rotation=45)
st.pyplot(fig)

# Tampilkan dataset
st.subheader('Data')
st.write(data)
