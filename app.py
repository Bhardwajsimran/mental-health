import streamlit as st
import numpy as np
import pandas as pd
import joblib

# =========================
# LOAD MODEL
# =========================
model = joblib.load("iris_model.pkl")
scaler = joblib.load("iris_scaler.pkl")

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Iris Classifier",
    page_icon="🌸",
    layout="centered"
)

st.title("🌸 Iris Flower Prediction App")
st.write("Enter flower measurements below:")

st.markdown("---")

# =========================
# INPUTS
# =========================
sl = st.slider("Sepal Length (cm)", 4.0, 8.0, 5.1)
sw = st.slider("Sepal Width (cm)", 2.0, 5.0, 3.5)
pl = st.slider("Petal Length (cm)", 1.0, 7.0, 1.4)
pw = st.slider("Petal Width (cm)", 0.1, 3.0, 0.2)

# =========================
# FEATURE ENGINEERING
# =========================
sepal_ratio = sl / (sw + 1e-6)
petal_ratio = pl / (pw + 1e-6)
sepal_area = sl * sw
petal_area = pl * pw

input_data = pd.DataFrame([[
    sl, sw, pl, pw,
    sepal_ratio,
    petal_ratio,
    sepal_area,
    petal_area
]], columns=[
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
    "sepal_ratio",
    "petal_ratio",
    "sepal_area",
    "petal_area"
])

# =========================
# PREDICTION
# =========================
if st.button("🌼 Predict Species"):

    prediction = model.predict(scaler.transform(input_data))[0]

    st.markdown("## 🎯 Prediction Result")

    if prediction == "setosa":
        st.success(f"🌸 {prediction}")
    elif prediction == "versicolor":
        st.info(f"🌿 {prediction}")
    else:
        st.warning(f"🌺 {prediction}")

    st.markdown("---")
    st.write("### Input Data")
    st.dataframe(input_data)
