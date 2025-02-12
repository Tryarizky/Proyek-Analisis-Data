import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

all_df = pd.read_csv("bike_merge.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

st.write(
    """
    # Hasil Analisis Dataset Bike Sharing :bike:
    Pada analisis ini, akan menginterpretasikan beberapa hal
    yang mungkin dipertanyakan oleh pemilik bisnis.
    1. Pada musim apa jumlah penyewa sepeda paling banyak?
    2. Seberapa sering seorang pelanggaan melakukan sewa dalam beberapa bulan terakhir?
    3. Bagaimana pola jumlah sewa berdasarkan jam? 
       pada jam berapa sewa mengalami peningkatan?
    """
)

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

# Tambahkan CSS untuk mempercantik sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffccd5;  /* Warna Pink */
        }
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            color: #6a1b9a;
        }
        .sidebar-text {
            font-size: 14px;
            text-align: center;
            color: #333333;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    # Menampilkan rentang waktu secara statis dengan judul yang sama formatnya seperti bagian lain
    st.markdown("---")  # Garis pemisah
    st.markdown('<p class="sidebar-title">📅 Rentang Waktu Data</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Data ini diperoleh pada rentang waktu <b>01 Januari 2011</b> hingga <b>31 Desember 2012</b>.</p>', unsafe_allow_html=True)

    st.markdown("---")  # Garis pemisah
    st.markdown('<p class="sidebar-title">📌 Tentang Data</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Dataset ini berisi informasi penyewaan sepeda berdasarkan tren cuaca, waktu, dan pola penggunaan pelanggan.</p>', unsafe_allow_html=True)

    st.markdown("---")  # Garis pemisah
    st.markdown('<p class="sidebar-title">🌍 Sumber Data</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-text">Data diperoleh dari <a href="https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset" target="_blank">Kaggle</a>.</p>', unsafe_allow_html=True)



# ======================================================
# FUNGSI-FUNGSI PEMROSESAN DATA
# ======================================================

def create_daily_orders_df(df):
    """Membuat DataFrame jumlah pesanan harian."""
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt_daily": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt_daily": "order_count",
    }, inplace=True)
    
    return daily_orders_df

def create_byseason_df(df):
    """Membuat DataFrame jumlah pelanggan berdasarkan musim."""
    byseason_df = df.groupby(by="season_daily").cnt_daily.nunique().reset_index()
    byseason_df.rename(columns={
        "cnt_daily": "customer_count",
        "season_daily": "season"
    }, inplace=True)
    
    return byseason_df

byseason_df = create_byseason_df(all_df)
daily_orders_df = create_daily_orders_df(all_df)

tanggal_sekarang = all_df['dteday'].max()
def create_rf_df(df):
    rf_df = df.groupby(by="mnth_daily", as_index=False).agg({
        'dteday': lambda x: (tanggal_sekarang - x.max()).days,
        'cnt_daily': 'count'
    }).reset_index()

# Mengganti nama kolom
    rf_df = pd.DataFrame({
        'month': rf_df['mnth_daily'],  
        'recency': rf_df['dteday'],
        'frequency': rf_df['cnt_daily']
    })

# Menampilkan DataFrame RF
    return rf_df



st.markdown("### Demografi Pelanggan")
st.markdown("#### Jumlah Pelanggan Berdasarkan Musim :fallen_leaf: ")

fig, ax = plt.subplots(figsize=(20, 10))

colors1 = ["#D3D3D3", "#D3D3D3", "#FFC0CB", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y="customer_count",
    x="season",
    data=byseason_df.sort_values(by="customer_count", ascending=False),
    palette=colors1,
    ax=ax
)

# Tambahkan angka di atas setiap batang
for p in ax.patches:
    ax.text(
        p.get_x() + p.get_width() / 2,  # Posisi x (tengah batang)
        p.get_height(),  # Posisi y (di atas batang)
        f"{int(p.get_height())}",  # Label angka
        ha="center",  # Posisi teks ditengah
        va="bottom",  # Posisi teks di atas batang
        fontsize=14,  # Ukuran font
        fontweight="bold",  # Teks tebal
        color="black"  # Warna teks
    )

# Atur tata letak plot
ax.set_title("Jumlah Pelanggan Berdasarkan Musim", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=25)
ax.tick_params(axis='y', labelsize=20)

# Tampilkan plot menggunakan Streamlit
st.pyplot(fig)

st.markdown("#### Masing-masing angka pada plot mempresentasikan musim:")
st.markdown("1 -> Clear, Few clouds, Partly cloudy, Partly cloudy")
st.markdown("2 -> Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist")
st.markdown("3 -> Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds")
st.markdown("4 -> Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog")


def main1():
    st.markdown("#### Interpretasi untuk mengetahui musim dengan jumlah penyewa sepeda terbanyak")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 1"):
        st.success("Berdasarkan plot grafik di atas, jumlah pelanggan terbanyak terjadi pada musim **Light Snow**, **Light Rain + Thunderstorm + Scattered Clouds**, dan **Light Rain + Scattered Clouds**")
if __name__ == "__main__":
    main1()

# Create the RF DataFrame
rf_df = create_rf_df(all_df)

# Streamlit app
st.markdown("### Analisisis RF :mag: ")

# Display RF DataFrame
st.markdown("#### Recency dan Frequency Pada Setiap Bulan:")
st.write(rf_df)

# Metrics for average Recency and Frequency
avg_recency = round(rf_df.recency.mean(), 1)
avg_frequency = round(rf_df.frequency.mean(), 2)

# Display average Recency and Frequency
col1, col2 = st.columns(2)
with col1:
    st.metric("Average Recency (months)", value=avg_recency)

with col2:
    st.metric("Average Frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 15))

# recency
recency_df = rf_df.sort_values(by="recency", ascending=True).head(12)
colors_recency = ["#FFC0CB"] * len(recency_df)
sns.barplot(y="recency", x="month", data=recency_df, palette=colors_recency, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Bulan ke-", fontsize=30)
ax[0].set_title("By Recency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# frequency
frequency_df = rf_df.sort_values(by="frequency", ascending=False).head(12)
colors_frequency = ["#ADD8E6"] * len(frequency_df)
sns.barplot(y="frequency", x="month", data=frequency_df, palette=colors_frequency, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Bulan ke-", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

# Display plots
st.pyplot(fig)

def main2():
    st.markdown("#### Interpretasi untuk mengetahui intensitas persewaan dalam beberapa bulan terakhir")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 2"):
        st.success("Pada beberapa bulan terakhir, pelanggan melakukan penyewaan cukup sering yang dapat dilihat dari recency yang nilainya semakin rendah. Jumlah penyewa juga cukup banyak dalam beberapa bulan terakhir yang dapat dilihat dari nilai frekuensinya.")

if __name__ == "__main__":
    main2()


all_df['dteday'] = pd.to_datetime(all_df['dteday'])
all_df.set_index('dteday', inplace=True)

# Judul
st.markdown("### Pola Waktu Jumlah Penyewa Sepeda")

st.markdown(
    """
    <style>
        /* Menghilangkan background slider */
        [data-testid="stSlider"] > div {
            background: transparent !important;
        }
        
        /* Mengatur warna garis (track) slider menjadi biru soft */
        [data-testid="stSlider"] > div > div {
            background-color: #ADD8E6 !important; /* Warna biru soft (light blue) */
        }
        
        /* Mengatur warna bulatan (handle) menjadi pink soft */
        [data-testid="stSlider"] > div > div > div {
            background-color: #FFB6C1 !important; /* Warna pink soft (light pink) */
            border: 2px solid #FF69B4 !important; /* Border pink yang sedikit lebih terang */
        }
        /* Mengubah warna angka pada slider */
        [data-testid="stTickBarMin"], 
        [data-testid="stTickBarMax"],
        [data-testid="stTickBarValue"] {
            color: #444 !important; /* Warna abu-abu gelap untuk kontras */
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Pilih rentang jam menggunakan slider
selected_hour_range = st.slider("Pilih Rentang Jam", min_value=0, max_value=23, value=(0, 23))

# Memilih data sesuai dengan rentang jam yang dipilih
selected_data = all_df[(all_df['hr'] >= selected_hour_range[0]) & (all_df['hr'] <= selected_hour_range[1])]

# Plot grafik
plt.figure(figsize=(12, 6))
sns.lineplot(x=selected_data['hr'], y=selected_data['cnt_hourly'], ci=None, color="#FF69B4")
plt.title("Pola Jumlah Penyewa Sepeda Harian Berdasarkan Waktu")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Penyewa Sepeda Harian")
plt.xticks(rotation=45, ha='right')

st.pyplot(plt.gcf())

def main3():
    st.markdown("#### Interpretasi grafik untuk mengetahui pola waktu jumlah penyewa sepeda")

    # Tombol untuk menampilkan keterangan
    if st.button("Tampilkan Keterangan 3"):
        st.success("Jumlah penyewa sepeda rata-rata meningkat pada jam 16.00-17.00, artinya pelanggan banyak bermain sepeda di waktu sore.")

if __name__ == "__main__":
    main3()

# Tambahkan sedikit pemisah
st.markdown("---")

# Rekomendasi Strategis
st.header("📌 Keputusan Bisnis: Strategi Penyewaan Sepeda")

st.markdown("""
    <style>
        .card {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🚴‍♂️ Optimasi Ketersediaan Sepeda di Musim dengan Permintaan Tinggi")
st.markdown('<div class="card"> ✅ Menambah jumlah sepeda saat musim Light Snow dan Light Rain untuk lonjakan permintaan.</div>', unsafe_allow_html=True)
st.markdown('<div class="card"> ☔ Menyediakan perlengkapan tambahan seperti jas hujan agar pelanggan tetap nyaman.</div>', unsafe_allow_html=True)

st.markdown("### 🎯 Strategi Retensi Pelanggan Berdasarkan Tren Penyewaan")
st.markdown('<div class="card"> 🏅 Program loyalitas atau diskon bagi pelanggan yang sering menyewa.</div>', unsafe_allow_html=True)
st.markdown('<div class="card"> 📅 Promosi atau paket langganan jangka panjang untuk mempertahankan pelanggan tetap.</div>', unsafe_allow_html=True)

st.markdown("### 🕒 Penyesuaian Operasional Berdasarkan Pola Jam Penyewaan")
st.markdown('<div class="card"> ⏰ Menambah sepeda lebih banyak di sore hari (16.00-17.00) sesuai tren penyewaan.</div>', unsafe_allow_html=True)
st.markdown('<div class="card"> 🎟️ Diskon khusus untuk penyewaan sore guna meningkatkan transaksi.</div>', unsafe_allow_html=True)

st.markdown("### 🌟 Meningkatkan Pengalaman Pelanggan")
st.markdown('<div class="card"> 📱 Fitur pemesanan online dengan pre-booking di jam sibuk.</div>', unsafe_allow_html=True)
st.markdown('<div class="card"> 📍 Optimalisasi lokasi stasiun sepeda berdasarkan pola permintaan.</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; font-size: 14px; color: gray;">🚀 Analysis Business by Trya | © 2025</div>', unsafe_allow_html=True)
