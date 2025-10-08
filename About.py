import streamlit as st

st.set_page_config(page_title="Welcome | DBS Vision App", page_icon="🩸", layout="wide")

st.image("images/dbs.jpg", use_container_width=True)

st.title("Welcome to the DBS Vision App")

st.markdown("""
The DBS Vision App allows you to perform computer vision analysis of dried blood spot size and shape, using images obtained using a Revvity Panthera 9 puncher.

Use the sidebar to navigate between pages:


| Page | Description |
|------|--------------|
| **Configuration** | Understanding how to configure the app and determine the instrument-specific pixel-mm conversion factor. |
| **External Calibration** | Calculating the instrument-specific pixel-mm conversion factor using an external standard. |
| **Single Image Analysis** | Uploading and analysing single images of dried blood spots and viewing an annotated image. |
| **Multiple Image Analysis** | Analysing multiple images and exporting DBS quality metrics as a .csv file. |
| **Data Analysis** | Simple analysis of the .csv file to produce summary statistics on DBS quality and show DBS diameter distribution. |
| **Time Series Analysis** | Time series analysis of a .csv file to assess time-based trends in DBS quality. |

""")
            
st.subheader("Disclaimer")
st.markdown("""
- This application is intended for research and service evaluation only.
- You are solely responsible for ensuring that you have obtained all necessary permissions, consents, and approvals for uploading or analysing any data via this application.
- Although this tool uses images from a Revvity Panthera puncher, it is not developed, endorsed, or supported by Revvity.
- Use this software at your own risk.""")

st.subheader("Example data")
st.markdown("If you would like to explore the application without uploading your own images, you can download a zip file containing 28 images "
"(use mm_per_pixel = 0.0589) or a .csv file of 5000 rows of synthetic data.")

st.download_button(
    label="Download example image files",
    data=open("data/example_dbs.zip", "rb").read(),
    file_name="example_dbs.zip",
    mime="application/zip"
)

st.download_button(
    label="Download example .csv file for Data Analysis and Time Series Analysis",
    data=open('data/synthetic_spot_metrics.csv', "rb").read(),
    file_name="synthetic_spot_metrics.csv",
    mime="text/csv"
)

st.subheader("About the author")
st.markdown("""
This tool was developed by [Nick Flynn](https://www.linkedin.com/in/flynnn) of Cambridge University Hospitals NHS Foundation Trust.

For comments, suggestions, or questions please contact: [nick.flynn@nhs.net](mailto:nick.flynn@nhs.net)
            
If you use this application in a publication, please cite the following paper:
             
**A computer vision approach to the assessment of dried blood spot size and quality in newborn screening.**
Flynn N, Moat SJ, Hogg SL.
*Clin Chim Acta.* 2023;547:117418.  
[Read the paper](https://doi.org/10.1016/j.cca.2023.117418)
            
""")