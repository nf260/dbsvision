import streamlit as st

st.set_page_config(page_title="Welcome | DBS Vision App", page_icon="🩸", layout="wide")

st.image("images/dbs.jpg", use_container_width=True)

st.title("Welcome to the DBS Vision App")

st.markdown("""
The DBS Vision App allows you to perform computer vision analysis of dried blood spot size and shape, using images obtained using a Revvity Panthera puncher.

Use the sidebar to navigate between pages:
- Understanding how to configure the app and determine the instrument specific pixel-mm conversion factor
- Uploading and analysing single images of dried blood spots and viewing an annotated image
- Analysing multiple images and exporting DBS quality metrics as .csv file
- Simple analysis of the .csv file to produce summary statistics on DBS quality and show DBS diameter distribution
- Time series analysis of a .csv file to assess time

--- 
            
### ⚠️ Disclaimer
- This application is intended for research and service evaluation only.
- You are solely responsible for ensuring that you have obtained all necessary permissions, consents, and approvals for uploading or analysing any data via this application.
- Although this tool uses images from a Revvity Panthera puncher, it is not developed, endorsed, or supported by Revvity.
- Use this software at your own risk.

---

This tool was developed by [Nick Flynn](https://www.linkedin.com/in/flynnn) of Cambridge University Hospitals NHS Foundation Trust.

For comments, suggestions, or questions please contact: [nick.flynn@nhs.net](mailto:nick.flynn@nhs.net)
            
If you use this application in a publication, please cite the following paper:
             
**A computer vision approach to the assessment of dried blood spot size and quality in newborn screening.**
Flynn N, Moat SJ, Hogg SL.
*Clin Chim Acta.* 2023;547:117418.  
[Read the paper](https://doi.org/10.1016/j.cca.2023.117418)
            
""")