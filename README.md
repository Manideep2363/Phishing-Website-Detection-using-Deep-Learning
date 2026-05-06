# 🛡️ Phishing Website Detection using Deep Learning

> A production-ready deep learning system that detects phishing websites in real-time by analyzing structured URL features and behavioral patterns — with full model explainability powered by SHAP.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow)](https://www.tensorflow.org/)
[![Keras](https://img.shields.io/badge/Keras-Deep_Learning-red?logo=keras)](https://keras.io/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-blue)](https://scikit-learn.org/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-green)](https://shap.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Overview

**Phishing Website Detection using Deep Learning** is an end-to-end machine learning application that classifies URLs as phishing or legitimate using a neural network trained on 30+ engineered URL and behavioral features. The system combines a robust feature extraction pipeline with a deep learning classifier and integrates SHAP-based explainability to make every prediction fully interpretable.

Unlike black-box detection tools, this project surfaces *why* a URL is flagged — showing exactly which features (e.g., domain age, DNS records, redirect depth) contributed most to each prediction. A Streamlit web interface enables real-time URL analysis with interactive visualizations, making it practical for both end users and security researchers.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Deep Learning Classifier** | Neural network built with TensorFlow/Keras trained on structured URL features |
| 🔧 **Feature Engineering Pipeline** | Automated extraction of 30+ URL, domain, and behavioral attributes per URL |
| 📊 **SHAP Explainability** | DeepExplainer (with KernelExplainer fallback) for per-prediction feature attribution |
| ⚡ **Real-Time Detection** | Instant phishing probability score for any submitted URL |
| 📈 **Interactive Visualizations** | SHAP bar and dot summary plots rendered inline in the app |
| 🌐 **Streamlit Interface** | Clean web UI for URL input, prediction results, and feature analysis dashboard |
| 💾 **Cached Model Loading** | `@st.cache_resource` ensures the model and scaler load once per session |

---

## 📂 Dataset Information

| Property | Details |
|---|---|
| **Dataset** | URL-based phishing detection dataset (`urldata.csv`) |
| **Target Column** | `Label` — binary (1 = Phishing, 0 = Legitimate) |
| **Excluded Columns** | `Domain` (identifier, not a feature) |
| **Feature Count** | 30+ structured features per URL |
| **SHAP Background** | 200-sample subset of training data used for explainer initialization |

### Feature Categories

The dataset covers four categories of URL signals:

- **URL Structure** — IP address presence, URL length, URL depth, `@` symbol, path redirections, `https` in domain, tiny URL usage, prefix/suffix hyphens
- **Domain Properties** — DNS record existence, domain age, domain expiry period, web traffic rank (Tranco list)
- **Web Behavior** — HTTP redirect count (≥3 hops flagged), mouse-over effects, right-click disabling, web forwards (iframes)
- **Security Signals** — HTTPS misuse in domain netloc, short-lived domains, absence of DNS records

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Deep Learning** | TensorFlow 2.x / Keras |
| **ML Utilities** | Scikit-learn (`StandardScaler`, metrics) |
| **Explainability** | SHAP (`DeepExplainer`, `KernelExplainer`) |
| **Data Processing** | Pandas, NumPy |
| **Feature Extraction** | `urllib.parse`, `socket`, `whois`, `requests`, `re` |
| **Caching** | `functools.lru_cache` (DNS lookups), `joblib` (scaler serialization) |
| **Frontend** | Streamlit, Matplotlib |
| **Model Serialization** | Keras `.keras` format, `joblib` (`.pkl`) |

---

## 🏗️ Model Architecture

The classifier is a fully connected feedforward neural network trained on scaled, tabular URL features.

```
Input Layer  (30 features)
      │
      ▼
Dense Layer  → ReLU activation
      │
      ▼
Dense Layer  → ReLU activation
      │
      ▼
Dense Layer  → ReLU activation
      │
      ▼
Output Layer (1 neuron) → Sigmoid activation
      │
      ▼
Phishing Probability Score  [0.0 – 1.0]
      │
  > 0.5 → ⚠️ PHISHING
 ≤ 0.5  → ✅ LEGITIMATE
```

**Preprocessing:**
- All 30+ features are standardized using `StandardScaler` (fitted on training data, persisted as `scaler.pkl`)
- Input features are binary/integer signals — no text tokenization required
- Scaler is applied consistently at both training and inference time

---

## ⚙️ Installation

### Prerequisites

- Python 3.10 or higher
- The trained model file: `phishing_model.keras`
- The fitted scaler: `scaler.pkl`
- The dataset file: `urldata.csv` (for SHAP background initialization)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/phishing-detection-deep-learning.git
cd phishing-detection-deep-learning

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```
streamlit
tensorflow
scikit-learn
pandas
numpy
shap
matplotlib
joblib
requests
python-whois
```

---

## 🚀 Usage

```bash
# Launch the Streamlit app
streamlit run app.py
```

1. Open the app in your browser at `http://localhost:8501`
2. Enter any URL in the input field (default: `https://web.whatsapp.com/`)
3. Click **"Check URL"**
4. View:
   - **Phishing Probability** score (0–100%)
   - **Verdict** — Safe ✅ or Phishing Warning ⚠️
   - **Feature Analysis Table** — all 16 extracted feature values
   - **SHAP Summary Plot (Bar)** — feature importance ranking
   - **SHAP Summary Plot (Dot)** — feature impact distribution

**Example URLs to test:**
```
Legitimate : https://www.google.com
Legitimate : https://web.whatsapp.com/
Suspicious : http://secure-paypal-login.xyz/verify
Suspicious : http://192.168.1.1/admin/login
```

---

## 🔄 Project Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                       INPUT: Raw URL                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │       FEATURE EXTRACTION           │
          │                                    │
          │  URL Structure  │  Domain Props    │
          │  ─────────────  │  ────────────    │
          │  IP address     │  DNS record      │
          │  URL length     │  Domain age      │
          │  URL depth      │  Domain expiry   │
          │  @ symbol       │  Web traffic     │
          │  Redirections   │                  │
          │  HTTPS in domain│  Web Behavior    │
          │  Tiny URL       │  ────────────    │
          │  Prefix/Suffix  │  HTTP redirects  │
          │                 │  Mouse-over      │
          │                 │  Right-click     │
          │                 │  Web forwards    │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │        PREPROCESSING               │
          │   StandardScaler (fitted on train) │
          │   joblib.load('scaler.pkl')        │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │       DEEP LEARNING MODEL          │
          │   keras.models.load_model(...)     │
          │   Dense → Dense → Dense → Sigmoid  │
          │   Output: probability [0.0 – 1.0]  │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │        SHAP EXPLAINABILITY         │
          │   DeepExplainer (primary)          │
          │   KernelExplainer (fallback)       │
          │   Background: 200 training samples │
          └─────────────────┬─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    STREAMLIT OUTPUT                              │
│   Phishing Probability │ Verdict │ Feature Table │ SHAP Plots   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Results / Metrics

| Metric | Score |
|---|---|
| **ROC-AUC** | **87.4%** |
| **Precision** | **92%** |
| **Features Engineered** | 30+ URL, domain, and behavioral attributes |
| **SHAP Background Samples** | 200 (balanced subset from training data) |
| **Detection Threshold** | 0.5 (sigmoid output probability) |

### Key Findings

- **High precision (92%)** means the model produces very few false positives — legitimate sites are rarely flagged incorrectly, which is critical for user trust.
- **ROC-AUC of 87.4%** demonstrates strong discriminative ability between phishing and legitimate URLs across all classification thresholds.
- **DNS record absence** and **domain age** consistently emerged as the highest-impact SHAP features — newly registered domains with no DNS history are the strongest phishing indicators.
- **URL length < 54 characters** and **absence of `@` symbols** are among the top features for legitimate site classification.

---

## 🔍 SHAP Explainability

This project integrates SHAP (SHapley Additive exPlanations) to explain individual predictions — a critical requirement for any security-facing ML application.

### How It Works

```python
# Primary: DeepExplainer (optimized for neural networks)
explainer = shap.DeepExplainer(model, background_data)

# Fallback: KernelExplainer (model-agnostic)
explainer = shap.KernelExplainer(model.predict, background_data)

# Compute per-feature SHAP values for a given URL
shap_values = explainer.shap_values(features_scaled)
```

### Visualizations Available in the App

| Plot Type | What It Shows |
|---|---|
| **SHAP Bar Summary** | Mean absolute SHAP value per feature — overall feature importance ranking |
| **SHAP Dot Summary** | Per-sample SHAP value distribution — shows direction and magnitude of each feature's impact |

### Interpreted Features

```
Feature Name       │ High Value → Phishing Indicator
───────────────────┼──────────────────────────────────
IP Address         │ URL uses raw IP instead of domain
DNS Record         │ No DNS record found for domain
Domain Age         │ Domain registered very recently
URL Depth          │ Deep nested path structure
Web Forwards       │ Iframe-based invisible redirects
HTTP Redirects     │ Chain of 3+ redirect hops
Tiny URL           │ URL shortened via bit.ly, t.co etc.
Prefix/Suffix      │ Hyphen present in domain name
```

---

## 🔮 Future Improvements

- [ ] **Expand feature set** — Add NLP features from URL tokens and page content (title, meta tags)
- [ ] **Ensemble model** — Combine neural network with XGBoost or Random Forest for higher ROC-AUC
- [ ] **Real-time URL scanning** — Integrate VirusTotal or Google Safe Browsing API for live threat intelligence
- [ ] **Browser extension** — Deploy as a Chrome/Firefox extension for in-browser phishing detection
- [ ] **Streaming prediction** — Reduce latency for batch URL analysis use cases
- [ ] **Adversarial robustness** — Test and harden the model against adversarial URL crafting
- [ ] **Cloud deployment** — Deploy on AWS Lambda or GCP Cloud Run with a REST API endpoint
- [ ] **Automated retraining** — Set up a pipeline to retrain on fresh phishing datasets (PhishTank, OpenPhish)
- [ ] **Threshold tuning** — Add configurable decision threshold with precision/recall trade-off display

---

## 👤 Author

**Manideep Vanne**
AI/ML Engineer | Hyderabad, India

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/manideep-vanne)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/manideepvanne)
[![Email](https://img.shields.io/badge/Email-Contact-red?logo=gmail)](mailto:vannemanideep@gmail.com)

---

> ⭐ If this project helped you, please consider giving it a star — it helps others in the security and ML community discover it!
