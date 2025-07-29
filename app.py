import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import streamlit.components.v1 as components

# Enhanced Google Analytics implementation
def inject_google_analytics():
    """Inject Google Analytics with enhanced tracking"""
    ga_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <!-- Global site tag (gtag.js) - Google Analytics -->
      <script async src="https://www.googletagmanager.com/gtag/js?id=G-5XZ4PKNX7D"></script>
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        
        // Configure Google Analytics
        gtag('config', 'G-5XZ4PKNX7D', {
          page_title: 'Electricity Bill Predictor',
          page_location: window.location.href,
          custom_map: {'custom_parameter_1': 'app_version'}
        });
        
        // Function to track custom events
        window.trackEvent = function(action, category, label, value) {
          gtag('event', action, {
            event_category: category,
            event_label: label,
            value: value
          });
        };
        
        // Track page load
        gtag('event', 'page_view', {
          page_title: 'Electricity Bill Predictor',
          page_location: window.location.href
        });
      </script>
    </head>
    <body>
      <div style="font-size:10px; color:#888; text-align:center;">Analytics Active</div>
    </body>
    </html>
    """
    components.html(ga_code, height=30)

# Initialize Google Analytics
inject_google_analytics()

# Custom event tracking function
def track_prediction_event(fan_hours, ac_hours, geyser_hours, residents, weather, prediction):
    """Track prediction events with custom parameters"""
    tracking_code = f"""
    <script>
      if (typeof gtag !== 'undefined') {{
        gtag('event', 'bill_prediction', {{
          event_category: 'prediction',
          event_label: 'electricity_bill',
          custom_parameters: {{
            fan_hours: {fan_hours},
            ac_hours: {ac_hours},
            geyser_hours: {geyser_hours},
            residents: {residents},
            weather: '{weather}',
            predicted_amount: {prediction:.2f}
          }}
        }});
      }}
    </script>
    """
    components.html(tracking_code, height=0)

# Load your trained model
try:
    model = joblib.load("electricity_bill_model.pkl")
except FileNotFoundError:
    st.error("Model file not found. Please ensure 'electricity_bill_model.pkl' exists.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Electricity Bill Predictor", 
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Main title and description
st.title("⚡ Electricity Bill Prediction")
st.markdown("Enter your household usage details below to get an estimated monthly electricity bill:")

# Create columns for better layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Appliance Usage")
    fan_hours = st.slider("Fan Usage (hours/day)", 0, 24, 5, help="Average daily hours of fan usage")
    ac_hours = st.slider("AC Usage (hours/day)", 0, 24, 2, help="Average daily hours of AC usage")
    geyser_hours = st.slider("Geyser Usage (hours/day)", 0, 24, 1, help="Average daily hours of geyser usage")
    fridge_on = st.selectbox("Fridge Status", ["Yes", "No"], help="Is your refrigerator running?")

with col2:
    st.subheader("🏡 Household Details")
    residents = st.number_input("Number of Residents", min_value=1, max_value=15, value=4, help="Total people living in the house")
    weather = st.selectbox("Weather Condition", ["Cold", "Moderate", "Hot"], index=1, help="Predominant weather in your area")
    day = st.slider("Day of Month (1–31)", 1, 31, 15, help="Current day of the month")

# Add some spacing
st.markdown("---")

# Encode inputs for the model
fridge_encoded = 1 if fridge_on == "Yes" else 0
weather_encoded = {"Cold": 1, "Moderate": 2, "Hot": 3}[weather]

# Prepare input data for prediction
input_data = pd.DataFrame([[fan_hours, ac_hours, geyser_hours, fridge_encoded, residents, weather_encoded, day]],
                          columns=["Fan_Hours", "AC_Hours", "Geyser_Hours", "Fridge_On", "Residents", "Weather", "Day"])

# Prediction button and results
st.subheader("💡 Get Your Bill Prediction")

if st.button("🔮 Predict Monthly Bill", type="primary", use_container_width=True):
    try:
        # Make prediction
        prediction = model.predict(input_data)
        predicted_amount = prediction[0]
        
        # Display main result
        st.success(f"💰 **Estimated Monthly Bill: ₹{predicted_amount:.2f}**")
        
        # Track the prediction event in Google Analytics
        track_prediction_event(fan_hours, ac_hours, geyser_hours, residents, weather, predicted_amount)
        
        # Show detailed breakdown
        with st.expander("📊 View Usage Breakdown", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**⚡ Daily Appliance Usage:**")
                st.write(f"• Fan: {fan_hours} hours/day")
                st.write(f"• Air Conditioner: {ac_hours} hours/day") 
                st.write(f"• Geyser: {geyser_hours} hours/day")
                st.write(f"• Refrigerator: {'Always On' if fridge_encoded else 'Off'}")
                
            with col2:
                st.markdown("**🏠 Household Information:**")
                st.write(f"• Number of Residents: {residents}")
                st.write(f"• Weather Condition: {weather}")
                st.write(f"• Calculation Day: {day}")
                
        # Additional insights
        st.info("💡 **Tip:** Your electricity bill can vary based on local tariff rates, seasonal changes, and actual usage patterns.")
        
        # Cost breakdown estimation (approximate)
        total_daily_hours = fan_hours + ac_hours + geyser_hours + (24 if fridge_encoded else 0)
        avg_cost_per_hour = predicted_amount / (total_daily_hours * 30) if total_daily_hours > 0 else 0
        
        if total_daily_hours > 0:
            st.markdown("### 📈 Estimated Cost Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Daily Usage", f"{total_daily_hours} hours")
            with col2:
                st.metric("Monthly Usage", f"{total_daily_hours * 30} hours")
            with col3:
                st.metric("Avg Cost/Hour", f"₹{avg_cost_per_hour:.2f}")
                
    except Exception as e:
        st.error(f"❌ Prediction failed: {str(e)}")
        st.info("Please check if your model file is properly trained and saved.")

# Sidebar with additional information
with st.sidebar:
    st.header("ℹ️ About This App")
    st.markdown("""
    This electricity bill predictor uses machine learning to estimate your monthly electricity costs based on:
    
    • **Appliance Usage**: Fan, AC, Geyser, Refrigerator
    • **Household Size**: Number of residents
    • **Weather Conditions**: Affects cooling/heating needs
    • **Time Factor**: Day of month for billing cycles
    
    **Note**: Predictions are estimates and actual bills may vary based on local electricity rates and usage patterns.
    """)
    
    st.header("🔧 Model Information")
    st.markdown("""
    • **Algorithm**: Linear Regression
    • **Features**: 7 input parameters
    • **Currency**: Indian Rupees (₹)
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
        <p>⚡ Electricity Bill Predictor v1.0 | Made with Streamlit</p>
        <p>This app uses Google Analytics to improve user experience and track usage patterns.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Optional: Add some CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        background-color: #ff6b6b;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #ff5252;
        color: white;
    }
    
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)