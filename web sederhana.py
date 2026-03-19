import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="DataInsight Dashboard",
    layout="wide",
    page_icon="📊"
)

# =========================
# 🎨 STYLE
# =========================
st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 700;
}
.subtitle {
    color: #6c757d;
    font-size: 15px;
}
.card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
.section-title {
    margin-top: 30px;
    font-size: 22px;
    font-weight: 600;
}
.small-note {
    color: gray;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔝 HEADER
# =========================
col1, col2 = st.columns([3,1])

with col1:
    st.markdown('<div class="main-title">📊 DataInsight Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analisis data otomatis, cepat, dan informatif</div>', unsafe_allow_html=True)

with col2:
    file = st.file_uploader("Upload Data", type=["csv", "xlsx"])

st.divider()

# =========================
# 🔧 LOAD DATA
# =========================
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        encodings = ['utf-8', 'latin1', 'cp1252']
        seps = [',', ';', '\t']

        for enc in encodings:
            for sep in seps:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding=enc, sep=sep)
                    if df.shape[1] > 1:
                        return df
                except:
                    continue
    else:
        return pd.read_excel(file)

    return None

# =========================
# 🚀 MAIN APP
# =========================
if file:
    df = load_data(file)

    if df is None:
        st.error("❌ File tidak bisa dibaca")
        st.stop()

    # Sampling jika data besar
    if len(df) > 50000:
        df = df.sample(50000, random_state=42)
        st.warning("⚡ Dataset besar → menggunakan 50.000 sampel")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # =========================
    # 📊 KPI
    # =========================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f'<div class="card"><h4>📄 Baris</h4><h2>{len(df):,}</h2></div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="card"><h4>📊 Kolom</h4><h2>{len(df.columns)}</h2></div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="card"><h4>❗ Missing</h4><h2>{df.isnull().sum().sum():,}</h2></div>', unsafe_allow_html=True)

    # =========================
    # 📋 DATA PREVIEW
    # =========================
    st.markdown('<div class="section-title">📋 Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)

    # =========================
    # 📈 STATISTIK
    # =========================
    st.markdown('<div class="section-title">📈 Statistik Deskriptif</div>', unsafe_allow_html=True)

    if numeric_cols:
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    else:
        st.warning("Tidak ada kolom numerik")

    # =========================
    # 📊 VISUALISASI
    # =========================
    st.markdown('<div class="section-title">📊 Visualisasi</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if numeric_cols:
            num_col = st.selectbox("Pilih Kolom Numerik", numeric_cols)
            fig = px.histogram(df, x=num_col, title=f"Distribusi {num_col}")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if cat_cols:
            cat_col = st.selectbox("Pilih Kolom Kategori", cat_cols)
            data = df[cat_col].value_counts().reset_index()
            data.columns = [cat_col, "Jumlah"]

            fig = px.bar(data, x=cat_col, y="Jumlah", title=f"Distribusi {cat_col}")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🧠 INSIGHT OTOMATIS
    # =========================
    st.markdown('<div class="section-title">🧠 Insight Otomatis</div>', unsafe_allow_html=True)

    st.info(f"Dataset memiliki {len(df):,} baris dan {len(df.columns)} kolom")

    # Numerik Insight
    if numeric_cols:
        st.markdown("#### 📊 Ringkasan Numerik")

        for col in numeric_cols[:3]:
            mean = df[col].mean()
            std = df[col].std()

            st.write(f"**{col}** → mean {mean:,.2f}, min {df[col].min():,.2f}, max {df[col].max():,.2f}")

            if std > mean:
                st.warning(f"{col}: Variasi tinggi")
            else:
                st.success(f"{col}: Relatif stabil")

    # Kategori Insight
    if cat_cols:
        st.markdown("#### 🏆 Kategori Dominan")

        for col in cat_cols[:2]:
            top = df[col].value_counts().idxmax()
            pct = df[col].value_counts(normalize=True).max() * 100

            st.write(f"{col} didominasi oleh **{top}** ({pct:.1f}%)")

    # Missing Insight
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) > 0:
        st.markdown("#### ⚠️ Data Quality")

        for col in missing.sort_values(ascending=False).head(3).index:
            pct = (missing[col] / len(df)) * 100
            st.write(f"{col} memiliki {pct:.1f}% data kosong")

    # Pola Data
    if numeric_cols:
        st.markdown("#### 🔍 Pola Data")

        max_col = df[numeric_cols].sum().idxmax()
        var_col = df[numeric_cols].std().idxmax()

        st.write(f"Total terbesar: **{max_col}**")
        st.write(f"Variasi tertinggi: **{var_col}**")

    # =========================
    # 💡 REKOMENDASI
    # =========================
    st.markdown('<div class="section-title">💡 Rekomendasi</div>', unsafe_allow_html=True)

    st.write("- Fokus pada variabel dengan variasi tinggi")
    st.write("- Tangani missing value sebelum analisis lanjutan")
    st.write("- Gunakan visualisasi untuk eksplorasi lebih dalam")

else:
    st.info("⬆️ Upload dataset untuk memulai analisis")