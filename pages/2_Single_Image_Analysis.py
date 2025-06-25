import streamlit as st
import numpy as np
import cv2
from joblib import load

from functions import (
    bs_detect,
    bs_detect_newPanthera,
    spot_metrics,
    calc_multispot_prob,
    draw_bs_contours,
    draw_bounding_box
)

st.title("DBS Vision - Single image analysis")

# === Parameter Section 1: ROI ===
st.header("1. Parameters")

st.markdown(
    "Conversion between pixels and mm. For more detail of how to determine the correct value for your instrument visit the "
    "[Configuration page](./Configuration)")
st.markdown("As a rough guide use **0.12** for images with size **752 x 480** and **0.06** for images with size **1440 × 920**"
)
mm_per_pixel = st.number_input("mm per pixel", value=0.1161, format="%.4f")


# === Upload Image Section ===
st.header("2. Upload Image")
st.write("This should be an original image from the Panthera puncher")
uploaded_file = st.file_uploader("Upload a .jpg/.jpeg/.png image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Load models
    scaler = load('log_model_scaler_220828.joblib')
    log_model = load('log_model_final_220828.joblib')

    # Define columns
    cols = ['contour_index','area','perimeter_mm','roundness','equiv_diam_mm', 
            'long_mm','short_mm', 'elongation', 'circular_extent',
            'hull_area', 'solidity', 'hull_perimeter', 'convexity', 
            'number_punches', 'average_punch_area']
    ml_cols = ['roundness','elongation','circular_extent','solidity','convexity']

    image_shape = img.shape
    image_width = image_shape[1]
    if image_width == 752:

        # Default coordinates for outer rectangle:
        x_min=1
        x_max=459
        y_min=50
        y_max=299

        # Default coordinates and radius for search area

        center = (209,139)
        radius = 68

        img = img[0:300, 150:610]
 
        # Run processing pipeline
        contours, hierarchy = bs_detect(img, x_min, x_max, y_min, y_max, select_punched=True)
    
    elif image_width == 1440:

         # Default coordinates for outer rectangle
        # This rectangle defines the region that the blood spot must fall completely within
        x_min=5
        x_max=900
        y_min=50
        y_max=575

        # Default coordinates and radius for search area - these may need tweaking depending on the configuration of the Panthera puncher
        center = (461,226)
        radius = 130
    
        img = img[0:580, 250:1160]

        contours, hierarchy = bs_detect_newPanthera(img, x_min, x_max, y_min, y_max, select_punched=True)

    else:
        st.warning(f"Incorrect image width, expect 1440 or 752, got {image_width}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    spot_met = spot_metrics(contours, hierarchy, mm_per_pixel, center, radius, select_punched=True)
    prob_ms_list = calc_multispot_prob(spot_met, cols, ml_cols, scaler, log_model)
    contour_img = draw_bs_contours(img_rgb.copy(), contours, hierarchy, center, radius, select_punched=True)
    bounding_box_img = draw_bounding_box(
        contour_img.copy(),
        contours,
        hierarchy,
        center,
        radius,
        spot_met,
        multispot_prob_list=prob_ms_list,
        select_punched=True,
        diam_range=(8, 16),
        prob_multi_limit=0.50
    )

    st.header("3. Output")

    diameter = round(spot_met[0][4], 1)
    ms_prob = round(prob_ms_list[0][1], 3)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("DBS Diameter (mm)", f"{diameter}")

    with col2:
        st.metric("Incorrect Blood Application Probability", f"{ms_prob}")

    with col3:
        st.metric("Image shape", f"{image_shape[1]} x {image_shape[0]}")

    st.image(bounding_box_img, channels="RGB", use_container_width=True)
    


else:
    st.info("Awaiting image upload...")
