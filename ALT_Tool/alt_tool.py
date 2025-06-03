# Accelerated Life Testing Tool (Streamlit Version)

import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

# Constants
k = 8.617e-5  # Boltzmann constant (eV/K)

st.set_page_config(page_title="ALT Tool", layout="centered")

st.title("Accelerated Life Testing Tool")

st.markdown("### Input Parameters")
col1, col2 = st.columns(2)

with col1:
    T_use_C = st.number_input("Use Temperature (°C)", value=25.0, step=5.0)
    RH_use = st.number_input("Use Relative Humidity (%)", value=50.0, step=5.0)
    Ea = st.number_input("Activation Energy Ea (eV)", value=0.9, step=0.1)
    confidence = st.number_input("Confidence Interval (CI)", value=0.9, min_value=0.7, max_value=0.99)
    reliability = st.number_input("Reliability Target (R)", value=0.9, min_value=0.7, max_value=0.99)
    beta = st.number_input("Weibull Beta", value=1.0, step=1.0)

with col2:
    T_stress_C = st.number_input("Stress Temperature (°C)", value=85.0, step=5.0)
    RH_stress = st.number_input("Stress Relative Humidity (%)", value=85.0, step=5.0)
    n = st.number_input("Humidity Exponent (Peck, n)", value=3.0, step=0.5)
    m = st.number_input("Humidity Exponent (Eyring, m)", value=2.0, step=0.5)
    D_uv = st.number_input("UV Derating Factor (D_UV)", value=0.8)
    D_tc = st.number_input("Thermal Cycling Derating Factor (D_TC)", value=0.9)
    D_mech = st.number_input("Mechanical Derating Factor (D_MECH)", value=0.95)

# Target life in hours (10 years default)
L = st.number_input("Target Life (Hours)", value=24*365*10, step=1000)

# Convert to Kelvin
T_use_K = T_use_C + 273.15
T_stress_K = T_stress_C + 273.15

st.markdown("### Acceleration Factor Formulas")
st.latex(r'''AF_{\text{Arrhenius}} = e^{\frac{E_a}{k} \left( \frac{1}{T_u} - \frac{1}{T_s} \right)}''')
st.latex(r'''AF_{\text{Peck}} = \left(\frac{RH_u}{RH_s}\right)^{-n} e^{\frac{E_a}{k} \left( \frac{1}{T_u} - \frac{1}{T_s} \right)}''')
st.latex(r'''AF_{\text{Eyring}} = \left(\frac{RH_s}{RH_u}\right)^{m} e^{\frac{E_a}{k} \left( \frac{1}{T_u} - \frac{1}{T_s} \right)}''')
st.latex(r'''AF_{\text{Eyring Total}} = AF_{\text{Eyring}} \cdot D_{UV} \cdot D_{TC} \cdot D_{MECH}''')

st.markdown("""
#### Notes:
- AF (Acceleration Factor) increases test stress to reduce test duration.
- L: Desired life (hours)
- CI: Confidence Interval (>=90%)
- R: Reliability Target (>=90%)
- n: Number of tested units (sample size)
- Derating factors apply only to Eyring Total and represent:
  - UV degradation
  - Thermal cycling
  - Mechanical stress

**References**:
- Peck Reference: 'A multi-stress Accelerated Life Test method for Smart Electricity Meters'
- MIL-HDBK-781A, Section 6.5 (Zero-Failure Tests)
- IEC 61709: Reliability Data Handbook(https://www.dinfo.unifi.it/upload/sub/laboratori/labmaq/labme_1/IEC_61709-extract.pdf)
- Accelerated Testing: Statistical Models, Test Plans, and Data Analyses (Nelson, 2004)
""")

st.markdown("### Zero-Failure Test Time Formulas")
st.markdown("Sample size formula for β = 1 (Exponential Distribution):")
st.latex(r'''n = \frac{L}{T \cdot AF} \cdot \frac{\ln(1 - CI)}{\ln(R)}''')
st.markdown("Test time formula when β ≠ 1 (Weibull Distribution):")
st.latex(r'''T = \left( \frac{L}{AF} \right) \cdot \frac{(-\ln(1 - CI))^{1/\beta}}{n^{1/\beta}}''')

st.markdown("""
### Zero-Failure Test Concepts: Exponential vs Weibull

In accelerated life testing, **zero-failure tests** are commonly used to validate the required lifetime with a given confidence and reliability level without observing any failures during the test period.

#### When Beta (β) = 1: Exponential Model
- The exponential distribution assumes **a constant failure rate** over time.
- This is commonly used for electronic components with no aging effects (i.e., early failures have been screened out).

#### When Beta (β) ≠ 1: Weibull Model
- The Weibull distribution allows modeling of **increasing or decreasing failure rates**.
  - β < 1: Early failures (infant mortality)
  - β > 1: Wear-out mechanisms
- This model gives more flexibility and realism for mechanical or physical degradation processes.
""")

# --- AF Calculations ---
AF_arrhenius = math.exp((Ea/k) * ((1/T_use_K) - (1/T_stress_K)))
AF_peck = ((RH_use / RH_stress)**(-n)) * math.exp((Ea/k) * ((1/T_use_K) - (1/T_stress_K)))
AF_eyring = ((RH_stress / RH_use)**(m)) * math.exp((Ea/k) * ((1/T_use_K) - (1/T_stress_K)))
AF_eyring_total = AF_eyring * D_uv * D_tc * D_mech

# --- Test Time ---
T_arrhenius = L / AF_arrhenius
T_peck = L / AF_peck
T_eyring = L / AF_eyring
T_eyring_total = L / AF_eyring_total

st.markdown("Simple Required Test Time Calculation: T = L / AF")
# Display AF Results
models_df = pd.DataFrame({
    "Model": ["Arrhenius", "Peck", "Eyring", "Eyring + Derating"],
    "AF": [AF_arrhenius, AF_peck, AF_eyring, AF_eyring_total],
    "Required Test Time (hr)": [T_arrhenius, T_peck, T_eyring, T_eyring_total],
    "Required Test Time (days)": [T_arrhenius/24, T_peck/24, T_eyring/24, T_eyring_total/24],
    "Rounded Days": [math.ceil(T_arrhenius/24), math.ceil(T_peck/24), math.ceil(T_eyring/24), math.ceil(T_eyring_total/24)]
})

st.markdown("### 1. Acceleration Factor & Required Test Time (Per Model)")
st.dataframe(models_df, hide_index=True)

# --- Sample Size Table Per Model ---
N_range = list(range(1, 31))

def test_time_exponential(N, AF):
    return (L / (N * AF)) * (math.log(1 - confidence) / math.log(reliability))

def test_time_weibull(N, AF):
    term = (-math.log(1 - confidence))**(1/beta)
    return (L / AF) * term / (N**(1/beta))

# Tabs per model
tabs = st.tabs(["Arrhenius", "Peck", "Eyring", "Eyring + Derating"])

for tab, name, AF in zip(tabs, ["Arrhenius", "Peck", "Eyring", "Eyring + Derating"], [AF_arrhenius, AF_peck, AF_eyring, AF_eyring_total]):
    with tab:
        st.markdown(f"### Required Test Time by Sample Size — {name} (Exponential Model, β = 1)")
        df_exp = pd.DataFrame({
            "Sample Size": N_range,
            "Test Time (hours)": [round(test_time_exponential(n, AF), 4) for n in N_range],
            "Test Time (days)": [round(test_time_exponential(n, AF)/24, 4) for n in N_range],
            "Rounded Days": [math.ceil(test_time_exponential(n, AF)/24) for n in N_range]
        })
        st.dataframe(df_exp, hide_index=True)

        st.markdown(f"### Required Test Time by Sample Size — {name} (Weibull Model, β ≠ 1)")
        df_weibull = pd.DataFrame({
            "Sample Size": N_range,
            "Test Time (hours)": [round(test_time_weibull(n, AF), 4) for n in N_range],
            "Test Time (days)": [round(test_time_weibull(n, AF)/24, 4) for n in N_range],
            "Rounded Days": [math.ceil(test_time_weibull(n, AF)/24) for n in N_range]
        })
        st.dataframe(df_weibull, hide_index=True)

st.markdown("""
**Note**: All models assume zero-failure criteria.
""")
