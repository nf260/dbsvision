import streamlit as st
import pandas as pd
import io
from PIL import Image

st.set_page_config(page_title="Multiple Image Analysis | DBS Vision App", page_icon="🩸", layout="wide")

st.title("Multiple image analysis")

from functions import spot_metrics_multi_uploaded, calc_multispot_prob_multi
from joblib import load

scaler = load('log_model_scaler_220828.joblib')
log_model = load('log_model_final_220828.joblib') 

### Define columns
ml_cols = ['roundness','elongation','circular_extent','solidity','convexity']
cols_to_show = ['file','sample_id','datetime','equiv_diam_mm','number_punches','pred_multi','prob_multi','mm_per_pixel']

st.markdown(
    "On this page you can analysis multiple image files. \n \n"
    "Enter mm per pixel. For more detail of how to determine the correct value for your instrument visit the "
    "[Configuration page](./Configuration). As a rough guide use **0.12** for images with size **752 x 480** and **0.06** for images with size **1440 × 920**"
)

# Main page input FIRST
mm_per_pix = st.number_input("🔧 mm per pixel", value=0.1161, format="%.4f")

uploaded_files = st.file_uploader(
    "Upload one or more image files from the Panthera puncher. All images must have the same size",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# Helper class to preserve file name on BytesIO
class NamedBytesIO(io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name


if uploaded_files:
    with st.spinner("Checking image sizes..."):
        sizes = []
        file_buffers = []

        for file in uploaded_files:
            data = file.read()
            buffer = NamedBytesIO(data, file.name)  # keep filename
            file_buffers.append(buffer)

            img = Image.open(io.BytesIO(data))
            sizes.append(img.size)

        unique_sizes = set(sizes)

        if len(unique_sizes) > 1:
            st.error(f"❌ Images have mixed sizes: {unique_sizes}. Please upload only one size at a time.")
            st.stop()

        # Only one size remains
        image_size = unique_sizes.pop()
        image_width = image_size[0]

        # Parameter sets
        if image_size == (752, 480):
            x_min, x_max, y_min, y_max = 1, 459, 50, 299
            center, radius = (209,139), 68

        elif image_size == (1440, 920):
            x_min, x_max, y_min, y_max = 5, 900, 50, 575
            center, radius = (461,226), 130

        else:
            st.error(f"❌ Unsupported image size: {image_size}. Only 752x480 or 1440x920 supported.")
            st.stop()

        # --- Check mm_per_pixel range ---
        expected_ranges = {
            752: (0.11, 0.13),
            1440: (0.05, 0.07)
        }
        if image_width in expected_ranges:
            lower, upper = expected_ranges[image_width]
            if not (lower <= mm_per_pix <= upper):
                st.warning(f"""
                ⚠️ mm per pixel is out of the expected range for {image_width}px images ({lower:.2f}–{upper:.2f}).  
                DBS diameter may be inaccurate.  
                Please check and review the [Configuration page](Configuration).
                """)

    # Now process
    with st.spinner("Processing images..."):
        df = spot_metrics_multi_uploaded(
            file_buffers, x_min, x_max, y_min, y_max,
            mm_per_pix, center, radius, image_size=f"{image_size[0]} x {image_size[1]}", select_punched=True
        )

        df = calc_multispot_prob_multi(df, ml_cols, scaler, model=log_model, scale=True)

        # Extract using regex
        df[['sample_id', 'date_str', 'time_str']] = df['file'].str.extract(
            r'^(.*)-(\d{8})-(\d{6})'
        )

        # Combine and convert to datetime
        df['datetime'] = pd.to_datetime(df['date_str'] + df['time_str'], format='%Y%m%d%H%M%S')
        df['mm_per_pixel'] = mm_per_pix
        df = df[cols_to_show]
    
    st.success(f"✅ Metrics calculated for {len(df)} images (size {image_size[0]}x{image_size[1]})!")
    st.dataframe(df)

    # Optional: CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download results as CSV", data=csv, file_name="spot_metrics.csv", mime='text/csv')

    st.markdown(
    "To analyse data in the .csv file, visit the [Data Analysis page](./Data_Analysis)."
    )

else:
    st.info("Upload one or more images to begin.")
