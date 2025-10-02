import streamlit as st

st.title("Configuration")

st.markdown("""
## Configuration of Pixel/mm Conversion Factor

When running the algorithm, an instrument-specific conversion factor between pixels and millimetres is used.

In our experience this factor is constant over the lifetime of the instrument however can vary between instruments.
            
This conversion can be determined in one of two ways:

---

### 1. Panthera Configuration File

For Panthera instruments with an image size of **752 × 480 pixels**, the conversion factor can be derived from information in the Panthera `config.xml` file:

- `CameraPixelXSizeInMillimeters`
- `CameraPixelYSizeInMillimeters`

Usually, these values are almost identical. We suggest using the **mean** of the two.

---

### 2. External Calibration Curve

For Panthera instruments with an image size of **1440 × 920 pixels**, using values from the `config.xml` file does **not** give accurate results.

Instead, the pixel-to-millimetre conversion factor should be determined by punching a circle of known diameter and using the [external calibration page](./External_Calibration).

If you would like to receive calibration material to determine a conversion factor, please contact: **nick.flynn@nhs.net**

---

## Validation of DBS Diameter Measurement

A validation set containing **anonymous images of 28 DBS printed on paper** is available to validate DBS diameter measurement.

If you would like to receive a copy, please contact: **nick.flynn@nhs.net**
""")