import streamlit as st
import numpy as np
import cv2

st.set_page_config(page_title="Calibration | DBS Vision App", page_icon="🩸", layout="wide")

st.title("External calibration")

from functions import (
    bs_detect,
    bs_detect_newPanthera,
    calibrate_mm_per_pixel_circle,
    draw_bs_contours)

st.markdown(
"On this page you can calculate the mm_per_pixel parameter for a Panthera puncher. \n \n" \
"Select the calibration material used to calibrate the Panthera measurement, then upload an image of that material. " \
"Note at present (October 2025) there is currently only one calibration material available"
)

# Dictionary of calibration materials and their radii
calibration_materials = {
    "C10 11/04/2025": 9.835,
    # Add more as needed
}

# Let user select
calibration_material_option = st.selectbox(
    "Select calibration material",
    options=list(calibration_materials.keys())
)

# Look up the corresponding radius
cal_radius = calibration_materials[calibration_material_option]

uploaded_file = st.file_uploader("Upload calibration image from the Panthera puncher", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

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

    # draw contours
    contour_img = draw_bs_contours(img_rgb.copy(),contours,hierarchy, center, radius, select_punched=True)

    st.image(contour_img, channels="RGB", use_container_width=True)

    mm_per_pixel = round(calibrate_mm_per_pixel_circle(contours,hierarchy, center, radius, cal_radius),4)

    st.markdown(
    "Make a note of the following parameter, which should be entered when analysing images from this Panthera using the algorithm")

    st.metric("Calculated mm per pixel", f"{mm_per_pixel}")

else:
    st.info("Awaiting image upload...")