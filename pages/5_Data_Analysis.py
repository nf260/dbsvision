import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Data analysis")

st.markdown(
"In this section you can analyse the .csv file obtained from the [Multiple Image Analysis page](./Multiple_Image_Analysis)."
)

# Filtering option
st.subheader("Data Selection")
filter_option = st.radio(
    "Select which data to include:",
    ["All rows", "First punch for each sample ID"],
    horizontal=True
)
# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)

    # Ensure datetime column is parsed correctly
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    if filter_option == "First punch for each sample ID":
        # Keep only the first record per sample_id based on earliest datetime
        df = df.sort_values(['sample_id', 'datetime']).drop_duplicates('sample_id', keep='first')

    # DBS Classification
    st.subheader("DBS classification")
    total_count = len(df)
    acceptable_count = len(df[(df['pred_multi'] == 'controls') & (df['equiv_diam_mm'] >= 8)])
    insufficient_count = len(df[(df['equiv_diam_mm'] < 8)])
    multispotted_count = len(df[(df['pred_multi'] == '0304') & (df['equiv_diam_mm'] >= 8)])

    acceptable_pct = round((acceptable_count/total_count)*100,2)
    insufficient_pct = round((insufficient_count/total_count)*100,2)
    multispotted_pct = round((multispotted_count/total_count)*100,2)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total DBS", f"{total_count}")
    
    with col2:
        st.metric("Acceptable DBS", f"{acceptable_count}")
        st.metric("Acceptable DBS (%)", f"{acceptable_pct}")
    
    with col3:
        st.metric("Small (< 8mm) DBS", f"{insufficient_count}")
        st.metric("Small (< 8mm) DBS (%)", f"{insufficient_pct}")
    
    with col4:
        st.metric("Multispotted DBS", f"{multispotted_count}")
        st.metric("Multispotted DBS (%)", f"{multispotted_pct}")

    # DBS diameter
    st.subheader("DBS diameter distribution")

    DBS_mean = round(df['equiv_diam_mm'].mean(), 2)
    DBS_median = round(df['equiv_diam_mm'].median(), 2)
    DBS_p25 = round(df['equiv_diam_mm'].quantile(0.25), 2)
    DBS_p75 = round(df['equiv_diam_mm'].quantile(0.75), 2)
    DBS_p5 = round(df['equiv_diam_mm'].quantile(0.05), 2)
    DBS_p95 = round(df['equiv_diam_mm'].quantile(0.95), 2)

    colA, colB = st.columns(2)

    with colA:
        st.metric("Mean DBS diameter (mm)", f"{DBS_mean}")
        st.metric("Median DBS diameter (mm)", f"{DBS_median}")
    with colB:
        st.metric("Interquartiles (mm)", f"{DBS_p25} – {DBS_p75}")
        st.metric("5th–95th centiles (mm)", f"{DBS_p5} – {DBS_p95}")

    fig, ax = plt.subplots()
    
    sns.ecdfplot(data=df, x='equiv_diam_mm', ax=ax)

    ax.axvline(x=8, color='red', linestyle='--', linewidth=1.5)
    ax.text(8, 0.05, '8 mm', color='red', rotation=90, va='bottom', ha='right')

    ax.axvline(x=DBS_mean, color='black', linestyle='--', linewidth=1, label=f'Mean = {DBS_mean} mm')
    ax.axvline(x=DBS_median, color='grey', linestyle='--', linewidth=1, label=f'Median = {DBS_median} mm')

    ax.set_title("DBS diameter distribution")
    ax.set_ylabel('Proportion of DBS')
    ax.set_xlabel('DBS diameter (mm)')
    ax.legend()

    st.pyplot(fig)

    # --- Download statistics ---
    st.subheader("Download summary statistics")
    stats = {
        "Total DBS": total_count,
        "Acceptable DBS": acceptable_count,
        "Acceptable DBS (%)": acceptable_pct,
        "Small (<8mm) DBS": insufficient_count,
        "Small (<8mm) DBS (%)": insufficient_pct,
        "Multispotted DBS": multispotted_count,
        "Multispotted DBS (%)": multispotted_pct,
        "Mean DBS diameter (mm)": DBS_mean,
        "Median DBS diameter (mm)": DBS_median,
        "25th percentile (mm)": DBS_p25,
        "75th percentile (mm)": DBS_p75,
        "5th percentile (mm)": DBS_p5,
        "95th percentile (mm)": DBS_p95,
    }

    stats_df = pd.DataFrame(stats.items(), columns=["Metric", "Value"])
    csv_data = stats_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download statistics as CSV",
        data=csv_data,
        file_name="dbs_summary_statistics.csv",
        mime="text/csv"
    )


