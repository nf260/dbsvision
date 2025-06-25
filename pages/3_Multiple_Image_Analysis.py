import streamlit as st
import pandas as pd

st.title("Multi image analysis")
st.warning("Please note so far this is only configured for images 752 x 480")


from functions import spot_metrics_multi_uploaded, calc_multispot_prob_multi

# Default coordinates for outer rectangle:
x_min=1
x_max=459
y_min=50
y_max=299

# Default coordinates and radius for search area

center = (209,139)
radius = 68

from joblib import load
scaler = load('log_model_scaler_220828.joblib')
log_model = load('log_model_final_220828.joblib') 

### Define columns

ml_cols = ['roundness','elongation','circular_extent','solidity','convexity']

cols_to_show = ['file','sample_id','datetime','equiv_diam_mm','number_punches','pred_multi','prob_multi']

uploaded_files = st.file_uploader(
    "Upload one or more image files",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# Sidebar inputs
st.sidebar.header("🔧 Configuration")

mm_per_pix = st.sidebar.number_input("mm per pixel", value=0.12)
select_punched = st.sidebar.checkbox("Only select punched spots", value=True)

# Run processing
if uploaded_files:
    with st.spinner("Processing images..."):
        df = spot_metrics_multi_uploaded(
            uploaded_files, x_min, x_max, y_min, y_max,
            mm_per_pix, center, radius, image_type='original', select_punched=True
        )

        df = calc_multispot_prob_multi(df,ml_cols,scaler,model=log_model,scale=True)

        # Extract using regex
        df[['sample_id', 'date_str', 'time_str']] = df['file'].str.extract(
        r'^([^-]+)-(\d{8})-(\d{6})'
        )

        # Combine and convert to datetime
        df['datetime'] = pd.to_datetime(df['date_str'] + df['time_str'], format='%Y%m%d%H%M%S')

        df = df[cols_to_show]
    
    st.success("✅ Metrics calculated!")
    st.dataframe(df)

    # Optional: CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download results as CSV", data=csv, file_name="spot_metrics.csv", mime='text/csv')
else:
    st.info("Upload one or more images to begin.")