import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import streamlit.components.v1 as components

# WORKING SOLUTION: Google Analytics with proper Streamlit integration
def inject_google_analytics():
    """Working Google Analytics implementation for Streamlit"""
    
    # Method 1: HTML head injection (most reliable)
    ga_script = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-5XZ4PKNX7D"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-5XZ4PKNX7D', {
        page_title: 'Electricity Bill Predictor',
        page_location: window.location.href,
        send_page_view: true
      });
      
      // Debug: Log to console
      console.log('Google Analytics loaded with ID: G-5XZ4PKNX7D');
    </script>
    """
    
    # Inject into page head using unsafe_allow_html
    st.markdown(ga_script, unsafe_allow_html=True)
    
    # Method 2: Additional component injection for backup
    ga_component = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-5XZ4PKNX7D"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', 'G-5XZ4PKNX7D', {{
                'page_title': 'Electricity Bill Predictor',
                'page_location': '{st.get_option("server.baseUrlPath") or ""}',
                'send_page_view': true
            }});
            
            // Make gtag available to parent window
            if (window.parent) {{
                window.parent.gtag = gtag;
                window.parent.dataLayer = dataLayer;
            }}
            
            console.log('GA Component loaded');
        </script>
    </head>
    <body>
        <div style="display:none;">GA Loaded</div>
    </body>
    </html>
    """
    
    # Use components.html as backup
    components.html(ga_component, height=1)

# Alternative: Google Tag Manager approach (more reliable for Streamlit)
def inject_google_tag_manager():
    """Google Tag Manager implementation (recommended for Streamlit)"""
    
    # You'll need to create a GTM container and replace GTM-XXXXXXX with your ID
    gtm_head = """
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
    <!-- End Google Tag Manager -->
    """
    
    gtm_body = """
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->
    """
    
    st.markdown(gtm_head, unsafe_allow_html=True)
    components.html(gtm_body, height=1)

# Track custom events
def track_prediction_event(fan_hours, ac_hours, geyser_hours, residents, weather, prediction):
    """Track prediction events"""
    
    event_script = f"""
    <script>
        // Wait for gtag to be available
        function trackPrediction() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'bill_prediction', {{
                    'event_category': 'predictions',
                    'event_label': 'electricity_bill',
                    'custom_parameters': {{
                        'fan_hours': {fan_hours},
                        'ac_hours': {ac_hours},
                        'geyser_hours': {geyser_hours},
                        'residents': {residents},
                        'weather': '{weather}',
                        'predicted_amount': {prediction:.2f}
                    }}
                }});
                console.log('Prediction event tracked');
            }} else if (window.parent && typeof window.parent.gtag !== 'undefined') {{
                window.parent.gtag('event', 'bill_prediction', {{
                    'event_category': 'predictions',
                    'event_label': 'electricity_bill',
                    'fan_hours': {fan_hours},
                    'ac_hours': {ac_hours},
                    'predicted_amount': {prediction:.2f}
                }});
                console.log('Prediction event tracked via parent');
            }} else {{
                console.warn('gtag not available for event tracking');
                // Retry after delay
                setTimeout(trackPrediction, 1000);
            }}
        }}
        
        trackPrediction();
    </script>
    """
    
    components.html(event_script, height=0)

# Initialize Google Analytics (choose one method)
inject_google_analytics()  # Primary method

# Uncomment this if you want to use GTM instead:
# inject_google_tag_manager()

# Load your trained model
try:
    model = joblib.load("electricity_bill_model.pkl")
except FileNotFoundError:
    st.error("❌ Model file not found. Please ensure 'electricity_bill_model.pkl' exists.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="⚡ Electricity Bill Predictor",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Electricity Bill Prediction")
st.markdown("Enter your household usage details below:")

# User inputs
col1, col2 = st.columns(2)

with col1:
    fan_hours = st.slider("Fan Usage (hours/day)", 0, 24, 5)
    ac_hours = st.slider("AC Usage (hours/day)", 0, 24, 2)
    geyser_hours = st.slider("Geyser Usage (hours/day)", 0, 24, 1)

with col2:
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
if st.button("🔮 Predict Bill", type="primary"):
    try:
        prediction = model.predict(input_data)
        predicted_amount = prediction[0]
        
        # Display result
        st.success(f"💰 **Estimated Monthly Bill: ₹{predicted_amount:.2f}**")
        
        # Track the prediction event
        track_prediction_event(fan_hours, ac_hours, geyser_hours, residents, weather, predicted_amount)
        
        # Show breakdown
        with st.expander("📊 Usage Breakdown", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**⚡ Daily Usage:**")
                st.write(f"• Fan: {fan_hours} hours")
                st.write(f"• AC: {ac_hours} hours")
                st.write(f"• Geyser: {geyser_hours} hours")
                st.write(f"• Fridge: {'Always On' if fridge_encoded else 'Off'}")
                
            with col2:
                st.markdown("**🏠 Household Info:**")
                st.write(f"• Residents: {residents}")
                st.write(f"• Weather: {weather}")
                st.write(f"• Day: {day}")
        
    except Exception as e:
        st.error(f"❌ Prediction failed: {str(e)}")

# Debug section (helpful for testing)
with st.expander("🔧 Analytics Debug"):
    st.markdown("""
    **Google Analytics Status:**
    - Property ID: `G-5XZ4PKNX7D`
    - Implementation: Direct gtag + Component backup
    
    **To verify it's working:**
    1. Open browser Developer Tools (F12)
    2. Go to Console tab
    3. Look for: `Google Analytics loaded with ID: G-5XZ4PKNX7D`
    4. Check Network tab for requests to `google-analytics.com`
    
    **Test in Google Analytics:**
    - Go to your GA dashboard
    - Check "Realtime" → "Overview"
    - You should see active users when testing
    """)
    
    # Test button for analytics
    if st.button("🧪 Test Analytics Event"):
        track_prediction_event(5, 2, 1, 4, "Moderate", 1500.00)
        st.info("Test event sent! Check your GA dashboard.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 12px;'>"
    "Made with ❤️ using Streamlit | Analytics: Google Analytics 4"
    "</div>", 
    unsafe_allow_html=True
)