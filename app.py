import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import streamlit.components.v1 as components

# Inject Google Analytics tracking tag into main page using full page width
components.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Google Analytics Embed</title>
      <!-- Global site tag (gtag.js) - Google Analytics -->
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-5XZ4PKNX7D"></script>
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-5XZ4PKNX7D');
      </script>
    </head>
    <body>
      <p style="font-size:12px;">Google Analytics Initialized</p>
    </body>
    </html>
    """,
    height=50  # Small but visible, avoids iframe blocking entirely
)


# Load your trained model (make sure you save it using joblib.dump)
model = joblib.load("electricity_bill_model.pkl")  # update with your actual model filename

st.set_page_config(page_title="Electricity Bill Predictor")
st.title("⚡ Electricity Bill Prediction")
st.markdown("Enter your household usage details below:")

# User inputs
fan_hours = st.slider("Fan Usage (hours/day)", 0, 24, 5)
ac_hours = st.slider("AC Usage (hours/day)", 0, 24, 2)
geyser_hours = st.slider("Geyser Usage (hours/day)", 0, 24, 1)
fridge_on = st.selectbox("Fridge On?", ["Yes", "No"])
residents = st.number_input("Number of Residents", min_value=1, max_value=15, value=4)
weather = st.selectbox("Weather Condition", ["Cold", "Moderate", "Hot"])
day = st.slider("Day of Month (1–31)", 1, 31, 15)

# Encode inputs
fridge_encoded = 1 if fridge_on == "Yes" else 0
weather_encoded = {"Cold": 1, "Moderate": 2, "Hot": 3}[weather]

# Prepare input data
input_data = pd.DataFrame([[fan_hours, ac_hours, geyser_hours, fridge_encoded, residents, weather_encoded, day]],
                          columns=["Fan_Hours", "AC_Hours", "Geyser_Hours", "Fridge_On", "Residents", "Weather", "Day"])


# Predict
if st.button("Predict Bill"):
    prediction = model.predict(input_data)
    st.success(f"Estimated Monthly Bill: ₹{prediction[0]:.2f}")
