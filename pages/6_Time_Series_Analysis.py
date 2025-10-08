import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Time Series Analysis, DBS Vision App", page_icon="🩸", layout="wide")

st.title("Time Series Analysis")

st.markdown("""
In this section you can perform time-based analysis of `.csv` file(s) obtained from the 
[Multiple Image Analysis page](./Multiple_Image_Analysis).  
You can explore DBS classification and diameter trends over time, 
and compare diameter distributions between time periods.
""")

# --- Upload CSV(s) ---
st.subheader("Data Upload")
uploaded_files = st.file_uploader(
    "Upload one or more CSV files",
    type=["csv"],
    accept_multiple_files=True
)

filter_option = st.radio(
    "Select which data to include:",
    ["All rows", "First punch for each sample ID"],
    horizontal=True
)

if uploaded_files:
    # Read and concatenate all uploaded CSVs
    df_list = []
    for file in uploaded_files:
        temp_df = pd.read_csv(file)
        df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

    if filter_option == "First punch for each sample ID":
        df = df.sort_values(['sample_id', 'datetime']).drop_duplicates('sample_id', keep='first')

    # --- CLASSIFICATION TRENDS ---
    st.header("Classification trends")
    class_group = st.selectbox(
        "Select time grouping for classification trends:",
        options=["Month", "Quarter", "Year"],
        index=1,
        key="class_group"
    )

    df_class = df.dropna(subset=['datetime']).copy()
    if class_group == "Month":
        df_class['period'] = df_class['datetime'].dt.to_period('M').dt.to_timestamp()
    elif class_group == "Quarter":
        df_class['period'] = df_class['datetime'].dt.to_period('Q').dt.to_timestamp()
    else:
        df_class['period'] = df_class['datetime'].dt.to_period('Y').dt.to_timestamp()

    class_summary = df_class.groupby('period').apply(
        lambda x: pd.Series({
            'Total DBS': len(x),
            'Acceptable DBS (%)': (len(x[(x['pred_multi'] == 'controls') & (x['equiv_diam_mm'] >= 8)]) / len(x)) * 100 if len(x) > 0 else 0,
            'Small DBS (<8mm) (%)': (len(x[x['equiv_diam_mm'] < 8]) / len(x)) * 100 if len(x) > 0 else 0,
            'Multispotted DBS (%)': (len(x[(x['pred_multi'] == '0304') & (x['equiv_diam_mm'] >= 8)]) / len(x)) * 100 if len(x) > 0 else 0
        })
    ).reset_index()

    st.dataframe(class_summary)

    fig_class, ax_class = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=class_summary, x='period', y='Acceptable DBS (%)', marker='o', label='Acceptable', ax=ax_class)
    sns.lineplot(data=class_summary, x='period', y='Small DBS (<8mm) (%)', marker='o', label='Small (<8mm)', ax=ax_class)
    sns.lineplot(data=class_summary, x='period', y='Multispotted DBS (%)', marker='o', label='Multispotted', ax=ax_class)
    ax_class.set_title(f"DBS classification trends by {class_group.lower()}")
    ax_class.set_ylabel("Percentage of DBS (%)")
    ax_class.set_xlabel(class_group)
    ax_class.set_ylim(0, 100)
    ax_class.legend()
    ax_class.tick_params(axis='x', rotation=45)
    st.pyplot(fig_class)

    csv_class = class_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download classification trends as CSV",
        data=csv_class,
        file_name=f"classification_trends_by_{class_group.lower()}.csv",
        mime="text/csv",
        key="download_class"
    )

    # --- DIAMETER TRENDS ---
    st.header("Diameter trends")
    diam_group = st.selectbox(
        "Select time grouping for diameter trends:",
        options=["Month", "Quarter", "Year"],
        index=1,
        key="diam_group"
    )

    df_diam = df.dropna(subset=['datetime']).copy()
    if diam_group == "Month":
        df_diam['period'] = df_diam['datetime'].dt.to_period('M').dt.to_timestamp()
    elif diam_group == "Quarter":
        df_diam['period'] = df_diam['datetime'].dt.to_period('Q').dt.to_timestamp()
    else:
        df_diam['period'] = df_diam['datetime'].dt.to_period('Y').dt.to_timestamp()

    diam_summary = df_diam.groupby('period').apply(
        lambda x: pd.Series({
            'Mean Diameter (mm)': x['equiv_diam_mm'].mean(),
            'Median Diameter (mm)': x['equiv_diam_mm'].median(),
            '25th Percentile (mm)': x['equiv_diam_mm'].quantile(0.25),
            '75th Percentile (mm)': x['equiv_diam_mm'].quantile(0.75),
            'Count': len(x)
        })
    ).reset_index()

    st.dataframe(diam_summary)

    fig_diam, ax_diam = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=diam_summary, x='period', y='Mean Diameter (mm)', marker='o', label='Mean', ax=ax_diam)
    sns.lineplot(data=diam_summary, x='period', y='Median Diameter (mm)', marker='o', label='Median', ax=ax_diam)
    ax_diam.fill_between(
        diam_summary['period'],
        diam_summary['25th Percentile (mm)'],
        diam_summary['75th Percentile (mm)'],
        color='lightgrey', alpha=0.4, label='IQR (25–75%)'
    )
    ax_diam.set_title(f"DBS diameter trends by {diam_group.lower()}")
    ax_diam.set_ylabel("DBS diameter (mm)")
    ax_diam.set_xlabel(diam_group)
    ax_diam.legend()
    ax_diam.tick_params(axis='x', rotation=45)
    st.pyplot(fig_diam)

    csv_diam = diam_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download diameter trends as CSV",
        data=csv_diam,
        file_name=f"diameter_trends_by_{diam_group.lower()}.csv",
        mime="text/csv",
        key="download_diam"
    )

    st.header("Diameter distribution by time period")

    st.markdown("By default, only the first, last and centre time period within each time grouping are shown. Specific periods can be added or removed as required")
    ecdf_group = st.selectbox(
        "Select time grouping for ECDF analysis:",
        options=["Month", "Quarter", "Year"],
        index=2,
        key="ecdf_group"
    )

    df_ecdf = df.dropna(subset=['datetime']).copy()
    if ecdf_group == "Month":
        df_ecdf['period'] = df_ecdf['datetime'].dt.to_period('M').astype(str)
    elif ecdf_group == "Quarter":
        df_ecdf['period'] = df_ecdf['datetime'].dt.to_period('Q').astype(str)
    else:
        df_ecdf['period'] = df_ecdf['datetime'].dt.to_period('Y').astype(str)

    # Filter out sparse periods (<10 samples)
    counts = df_ecdf['period'].value_counts()
    valid_periods = counts[counts > 10].index
    df_ecdf = df_ecdf[df_ecdf['period'].isin(valid_periods)]

    # --- Default selection: first, middle, and last period ---
    unique_periods = sorted(df_ecdf['period'].unique())
    if len(unique_periods) >= 3:
        mid_index = len(unique_periods) // 2
        default_periods = [unique_periods[0], unique_periods[mid_index], unique_periods[-1]]
    else:
        default_periods = unique_periods  # fewer than 3 available

    selected_periods = st.multiselect(
        "Select specific periods to compare:",
        options=unique_periods,
        default=default_periods,
        key="ecdf_periods"
    )

    df_ecdf_sel = df_ecdf[df_ecdf['period'].isin(selected_periods)]

    # --- ECDF plot ---
    fig_ecdf_time, ax_ecdf = plt.subplots(figsize=(10, 6))
    if df_ecdf_sel.empty:
        st.warning("No data available for selected periods.")
    else:
        palette = sns.color_palette("husl", len(selected_periods))
        for i, period in enumerate(selected_periods):
            subset = df_ecdf_sel[df_ecdf_sel['period'] == period]
            sns.ecdfplot(
                data=subset,
                x='equiv_diam_mm',
                ax=ax_ecdf,
                color=palette[i],
                label=period
            )

        # Add 8mm reference line
        ax_ecdf.axvline(x=8, color='red', linestyle='--', linewidth=1.5)
        ax_ecdf.text(8, 0.05, '8 mm', color='red', rotation=90, va='bottom', ha='right')

        ax_ecdf.set_title(f"DBS diameter ECDF by selected {ecdf_group.lower()}(s)")
        ax_ecdf.set_xlabel("DBS diameter (mm)")
        ax_ecdf.set_ylabel("Cumulative proportion")

        # Improved legend layout
        ax_ecdf.legend(
            title=f"{ecdf_group}(s)",
            bbox_to_anchor=(1.04, 1),
            loc='upper left',
            borderaxespad=0,
            fontsize='small'
        )
        plt.tight_layout(rect=[0, 0, 0.8, 1])  # leave room for legend

        st.pyplot(fig_ecdf_time)
