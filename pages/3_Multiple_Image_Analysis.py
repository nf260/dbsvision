import streamlit as st
import pandas as pd

st.title("Multi image analysis")

from functions import spot_metrics_multi_uploaded, calc_multispot_prob_multi

from joblib import load
scaler = load('log_model_scaler_220828.joblib')
log_model = load('log_model_final_220828.joblib') 

### Define columns

ml_cols = ['roundness','elongation','circular_extent','solidity','convexity']

cols_to_show = ['file','sample_id','datetime','equiv_diam_mm','number_punches','pred_multi','prob_multi','mm_per_pixel']

uploaded_files = st.file_uploader(
    "Upload one or more image files from the Panthera puncher. All images must have the same size",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# Sidebar inputs
st.sidebar.header("🔧 Configuration")

mm_per_pix = st.sidebar.number_input("mm per pixel", value=0.1161, format="%.4f")
image_size = st.sidebar.selectbox(label="Select image size",options=['752 x 480','1440 x 920'])

if image_size == '752 x 480':
        # Default coordinates for outer rectangle:
        x_min=1
        x_max=459
        y_min=50
        y_max=299

        # Default coordinates and radius for search area

        center = (209,139)
        radius = 68

elif image_size == '1440 x 920':
         # Default coordinates for outer rectangle
        # This rectangle defines the region that the blood spot must fall completely within
        x_min=5
        x_max=900
        y_min=50
        y_max=575

        # Default coordinates and radius for search area - these may need tweaking depending on the configuration of the Panthera puncher
        center = (461,226)
        radius = 130

else: 
    raise ValueError("Image size not supported")

# Run processing
if uploaded_files:
    with st.spinner("Processing images..."):

        df = spot_metrics_multi_uploaded(
            uploaded_files, x_min, x_max, y_min, y_max,
            mm_per_pix, center, radius, image_size=image_size, select_punched=True
        )

        df = calc_multispot_prob_multi(df,ml_cols,scaler,model=log_model,scale=True)

        # Extract using regex
        df[['sample_id', 'date_str', 'time_str']] = df['file'].str.extract(
        r'^([^-]+)-(\d{8})-(\d{6})'
        )

        # Combine and convert to datetime
        df['datetime'] = pd.to_datetime(df['date_str'] + df['time_str'], format='%Y%m%d%H%M%S')
        df['mm_per_pixel']=mm_per_pix
        df = df[cols_to_show]
    
    st.success("✅ Metrics calculated!")
    st.dataframe(df)

    # Optional: CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download results as CSV", data=csv, file_name="spot_metrics.csv", mime='text/csv')
else:
    st.info("Upload one or more images to begin.")