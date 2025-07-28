# ⚡ Electricity Bill Predictor

A simple and interactive Streamlit web app that predicts your monthly electricity bill based on household appliance usage and environmental conditions.

---

## 🔍 Overview

This project is a machine learning-based application built with Streamlit. It takes user inputs such as fan usage, AC usage, number of residents, and more to predict the electricity bill using a pre-trained Linear Regression model.

---

## 🚀 Live Demo

🔗 [View the Live App on Render](https://electricity-bill-predictor.onrender.com)  
*(Update this link after deployment)*

---

## 📦 Features

- User-friendly UI built using **Streamlit**
- Predicts monthly electricity bill based on:
  - Fan, AC, Geyser usage (hours/day)
  - Fridge On/Off
  - Number of Residents
  - Weather Conditions
  - Day of the Month
- Pre-trained ML model using **Linear Regression**

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**
- **Pandas**, **NumPy**
- **Scikit-learn**
- **Joblib** (for loading the saved ML model)

---

## 📁 Folder Structure


---

## 🧪 Example Inputs

| Feature             | Example |
|---------------------|---------|
| Fan Usage           | 5 hours/day |
| AC Usage            | 2 hours/day |
| Geyser Usage        | 1 hour/day |
| Fridge              | Yes |
| Residents           | 4 |
| Weather             | Moderate |
| Day of the Month    | 15 |

---

## 💻 Local Installation

```bash
git clone https://github.com/yourusername/electricity-bill-predictor.git
cd electricity-bill-predictor
pip install -r requirements.txt
streamlit run app.py
