import streamlit as st
import joblib
import pandas as pd
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Titanic Survival Predictor",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Model and Stats ---
@st.cache_resource
def load_model_and_stats():
    model_path = os.path.join(os.path.dirname(__file__), 'titanic_model.pkl')
    stats_path = os.path.join(os.path.dirname(__file__), 'stats.json')
    
    try:
        model = joblib.load(model_path)
        with open(stats_path) as f:
            stats = json.load(f)
        return model, stats
    except Exception as e:
        st.error(f"Error loading model or stats: {e}")
        return None, None

model, model_stats = load_model_and_stats()

if model is None or model_stats is None:
    st.error("Failed to load the model. Please check if 'titanic_model.pkl' and 'stats.json' exist in the root directory.")
    st.stop()

# --- Custom CSS (to inject some nice styling) ---
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1f77b4;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 20px;
        }
        .stat-box {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-header">🚢 Titanic Survival Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Machine Learning Model · Random Forest</div>', unsafe_allow_html=True)

# --- Display Model Stats ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-box">Model Accuracy<br><span class="stat-value">{model_stats["accuracy"]}%</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box">Passengers Trained<br><span class="stat-value">{model_stats["train_size"]}</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-box">Survival Rate<br><span class="stat-value">{model_stats["survived_pct"]}%</span></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-box">Algorithm<br><span class="stat-value">Random Forest</span></div>', unsafe_allow_html=True)

st.divider()

# --- Main Layout ---
col_form, col_result = st.columns([1, 1])

# --- Input Form ---
with col_form:
    st.subheader("Passenger Details")
    
    with st.container():
        pclass = st.selectbox("Passenger Class", options=[1, 2, 3], format_func=lambda x: f"{x}st Class" if x==1 else (f"{x}nd Class" if x==2 else f"{x}rd Class"))
        sex = st.radio("Gender", options=["male", "female"], horizontal=True)
        age = st.slider("Age", min_value=1.0, max_value=80.0, value=29.0, step=0.5)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sibsp = st.number_input("Siblings / Spouse", min_value=0, max_value=10, value=0)
        with col_f2:
            parch = st.number_input("Parents / Children", min_value=0, max_value=10, value=0)
            
        fare = st.slider("Fare (£)", min_value=0.0, max_value=500.0, value=32.0, step=0.5)
        embarked = st.selectbox("Port of Embarkation", options=["S", "C", "Q"], format_func=lambda x: "Southampton" if x=="S" else ("Cherbourg" if x=="C" else "Queenstown"))

# --- Processing & Prediction ---
sex_encoded = 1 if sex == 'male' else 0
embarked_map = {'S': 0, 'C': 1, 'Q': 2}
embarked_encoded = embarked_map.get(embarked, 0)

feature_names = ['Pclass', 'Sex_encoded', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked_encoded']
features = pd.DataFrame([[pclass, sex_encoded, age, sibsp, parch, fare, embarked_encoded]], columns=feature_names)

with col_result:
    st.subheader("Prediction Result")
    
    if st.button("Predict Fate", type="primary", use_container_width=True):
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        survival_prob = float(probability[1]) * 100
        death_prob = float(probability[0]) * 100
        
        if prediction == 1:
            st.success("The passenger is predicted to SURVIVE.")
            st.markdown("### SURVIVED ⚓")
        else:
            st.error("The passenger is predicted to NOT SURVIVE.")
            st.markdown("### PERISHED 🪦")
            
        st.write(f"**Survival Probability:** {survival_prob:.1f}%")
        st.progress(survival_prob / 100.0)
        
        st.write(f"**Death Probability:** {death_prob:.1f}%")
        st.progress(death_prob / 100.0)

    st.divider()
    
    st.subheader("Feature Importance")
    importances = model_stats.get("feature_importances", {})
    if importances:
        # Format importances for a chart
        imp_df = pd.DataFrame({
            "Feature": list(importances.keys()),
            "Importance": [val * 100 for val in importances.values()]
        }).sort_values(by="Importance", ascending=True)
        
        st.bar_chart(imp_df.set_index("Feature"), height=250)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Random Forest Classifier · Built with Streamlit + Scikit-learn</p>", unsafe_allow_html=True)
