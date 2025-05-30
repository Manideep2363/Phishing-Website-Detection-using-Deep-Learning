# -- coding: utf-8 --
import streamlit as st
import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import re
from urllib.parse import urlparse
import socket
from functools import lru_cache
import whois
from datetime import datetime
import requests
import joblib
import shap
import matplotlib.pyplot as plt
from streamlit.components.v1 import html

# Helper function for SHAP force plot
def st_shap(plot, height=None, width=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    html(shap_html, height=height, width=width)

# Load the trained model and scaler
@st.cache_resource
def load_model_and_scaler():
    model = keras.models.load_model('phishing_model.keras')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

try:
    model, scaler = load_model_and_scaler()
except:
    st.error("Model or scaler file not found. Please ensure 'phishing_model.keras' and 'scaler.pkl' are in the directory.")
    st.stop()

# Load some training data for SHAP background
@st.cache_data
def load_background_data():
    data = pd.read_csv('5.urldata.csv')  # Adjust path as needed
    X = data.drop(columns=['Domain', 'Label'])
    return scaler.transform(X[:200])  # Increased subset for better representation

background_data = load_background_data()

# Initialize SHAP explainer
@st.cache_resource
def get_shap_explainer():
    try:
        # Try DeepExplainer first
        return shap.DeepExplainer(model, background_data)
    except Exception as e:
        st.warning(f"DeepExplainer failed: {str(e)}. Falling back to KernelExplainer.")
        return shap.KernelExplainer(model.predict, background_data)

explainer = get_shap_explainer()

# Feature extraction functions
def has_ip_address(url):
    return 1 if re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1-3}\b', url) else 0

def has_at_symbol(url):
    return 1 if '@' in url else 0

def get_url_length(url):
    return 1 if len(url) < 54 else 0

def get_url_depth(url):
    path = urlparse(url).path
    if path == '/':
        return 0
    return path.count('/')

def has_redirection(url):
    return 1 if '//' in urlparse(url).path else 0

def has_https_in_domain(url):
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else 0

def is_tiny_url(url):
    tiny_domain = ["bit.ly", "goog.gl", "tinyurl.com", "ow.ly", "t.co"]
    domain = urlparse(url).netloc
    return 1 if domain in tiny_domain else 0

def has_prefix_suffix(url):
    domain = urlparse(url).netloc
    return 1 if '-' in domain else 0

@lru_cache(maxsize=10000)
def check_dns_record(domain):
    try:
        socket.gethostbyname(domain)
        return 1
    except socket.error:
        return 0

try:
    ranked_domains = pd.read_csv("tranco_Z38YG.csv")
except:
    ranked_domains = pd.DataFrame()
def get_web_traffic(domain):
    return 1 if domain in ranked_domains.values else 0

def get_domain_age(domain):
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age_in_days = (datetime.now() - creation_date).days
        return 1 if age_in_days >= 365 else 0
    except Exception:
        return 0

def get_domain_end_period(domain):
    try:
        domain_info = whois.whois(domain)
        expiration_date = domain_info.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        days_to_expire = (expiration_date - datetime.now()).days
        return 1 if days_to_expire >= 180 else 0
    except Exception:
        return 0

def has_mouse_over_effect(url):
    try:
        response = requests.get(url, timeout=5)
        html = response.text
        return 1 if 'onmouseover' in html else 0
    except Exception:
        return 0

def allows_right_click(url):
    return 1

def has_web_forwards(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=3)
        redirect_count = len(response.history)
        return 1 if redirect_count >= 3 else 0
    except Exception:
        return 0

def extract_features(url):
    url = url.rstrip('/')
    domain = urlparse(url).netloc
    features = [has_ip_address(url), has_at_symbol(url), get_url_length(url),
                get_url_depth(url), has_redirection(url), has_https_in_domain(url),
                is_tiny_url(url), has_prefix_suffix(url), check_dns_record(domain),
                get_web_traffic(domain), get_domain_age(domain), get_domain_end_period(domain),
                0, has_mouse_over_effect(url), allows_right_click(url), has_web_forwards(url)]
    return features

# Streamlit interface
st.title("Phishing URL Detector")
st.write("Enter a URL to check if it’s potentially a phishing site")

url_input = st.text_input("Enter URL", "https://web.whatsapp.com/")

def make_prediction_and_explain(url):
    try:
        features = np.array(extract_features(url))
        features_scaled = scaler.transform(features.reshape(1, -1))
        prediction = model.predict(features_scaled)
        shap_values = explainer.shap_values(features_scaled)
        # Reshape shap_values if necessary
        if isinstance(shap_values, list):
            shap_values = shap_values[0]  # For DeepExplainer with single output
        if len(shap_values.shape) == 3:
            shap_values = np.squeeze(shap_values, axis=-1)
        return prediction[0][0], features, shap_values, features_scaled
    except Exception as e:
        st.error(f"Error processing URL: {str(e)}")
        return None, None, None, None

if st.button("Check URL"):
    with st.spinner("Analyzing URL..."):
        prediction, features, shap_values, features_scaled = make_prediction_and_explain(url_input)
        
        if prediction is not None:
            st.subheader("Results")
            probability = prediction * 100
            st.write(f"Phishing Probability: {probability:.2f}%")
            st.write(f"Raw Prediction Value: {prediction}")
            
            if prediction > 0.5:
                st.error("WARNING: This URL is likely a phishing site!")
            else:
                st.success("SAFE: This URL appears to be legitimate")
            
            # Feature Analysis
            st.subheader("Feature Analysis")
            feature_names = [
                "IP Address", "At Symbol", "URL Length", "URL Depth", "Redirection",
                "HTTPS in Domain", "Tiny URL", "Prefix/Suffix", "DNS Record",
                "Web Traffic", "Domain Age", "Domain End Period", "Iframe",
                "Mouse Over", "Right Click", "Web Forwards"
            ]
            feature_df = pd.DataFrame({
                "Feature": feature_names,
                "Value": features
            })
            st.table(feature_df)
            
            # SHAP Explanation
            st.subheader("SHAP Explanation")
            st.write("This plot shows how each feature contributes to the prediction.")
            
            # Debug: Print SHAP values and shapes
            st.write("SHAP Values:", shap_values.tolist())  # Convert to list for display
            st.write("Features Scaled Shape:", features_scaled.shape)
            st.write("SHAP Values Shape:", shap_values.shape)
            
            # Check if SHAP values are non-zero
            if np.all(shap_values == 0):
                st.warning("SHAP values are all zero. The plot may be empty. This could indicate an issue with the explainer or model sensitivity.")
            
            st.write("SHAP Summary Plot (Bar):")
            try:
                fig, ax = plt.subplots()
                shap.summary_plot(shap_values, features_scaled, feature_names=feature_names, plot_type="bar", show=False)
                st.pyplot(fig)
                plt.close(fig)
            except Exception as e:
                st.error(f"Error rendering summary plot (bar): {str(e)}")
            
            # SHAP Summary Plot (Dot)
            st.write("SHAP Summary Plot (Dot):")
            try:
                fig, ax = plt.subplots()
                shap.summary_plot(shap_values, features_scaled, feature_names=feature_names, plot_type="dot", show=False)
                st.pyplot(fig)
                plt.close(fig)
            except Exception as e:
                st.error(f"Error rendering summary plot (dot): {str(e)}")

st.sidebar.title("About")
st.sidebar.write("""
This tool uses a neural network to detect phishing URLs based on features like:
- URL structure (length, depth, special characters)
- Domain properties (age, DNS records, traffic)
- Web behavior (redirects, mouse-over effects)
The SHAP plot explains feature contributions to the prediction.
""")