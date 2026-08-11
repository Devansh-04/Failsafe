import os
import io
from pathlib import Path

import joblib
import pandas as pd
import shap

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .schemas import StudentInput
from .intervention import generate_intervention_plan


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="FAILSAFE API",
    description="Student failure-risk prediction API using XGBoost and SHAP",
    version="1.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

# During local development:
#     http://localhost:5173
#
# On Render:
#     Set FRONTEND_URL as an environment variable to your
#     deployed frontend URL.

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODEL LOADING
# ============================================================

# Get the root directory of the project.
#
# File structure:
#
# FailSafe/
# ├── api/
# │   └── main.py
# ├── models/
# │   ├── failsafe_model.pkl
# │   └── failsafe_threshold.pkl
#
# Therefore:
# main.py -> parent = api/
# api/    -> parent = FailSafe/

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "failsafe_model.pkl"
THRESHOLD_PATH = MODEL_DIR / "failsafe_threshold.pkl"


# Load trained model and threshold
model = joblib.load(MODEL_PATH)
threshold = joblib.load(THRESHOLD_PATH)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "FAILSAFE API is running",
        "status": "ok"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ============================================================
# SINGLE STUDENT PREDICTION
# ============================================================

@app.post("/predict")
def predict_student_risk(student: StudentInput):

    student_dict = student.dict()

    input_df = pd.DataFrame([student_dict])

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    risk_probability = model.predict_proba(input_df)[0][1]

    prediction = int(risk_probability >= threshold)

    # --------------------------------------------------------
    # Extract preprocessing + XGBoost model from pipeline
    # --------------------------------------------------------

    preprocessor = model.named_steps["preprocessor"]
    xgb_model = model.named_steps["model"]

    # --------------------------------------------------------
    # Transform input using the same preprocessing pipeline
    # --------------------------------------------------------

    processed_input = preprocessor.transform(input_df)

    # Get feature names directly from the fitted preprocessor.
    # This is safer than manually reconstructing categorical
    # and numerical feature names.
    feature_names = preprocessor.get_feature_names_out()

    # Convert transformed data into a dense array if required.
    if hasattr(processed_input, "toarray"):
        processed_input = processed_input.toarray()

    processed_input = pd.DataFrame(
        processed_input,
        columns=feature_names
    )

    # --------------------------------------------------------
    # SHAP explanation
    # --------------------------------------------------------

    explainer = shap.TreeExplainer(xgb_model)

    shap_values = explainer.shap_values(processed_input)

    # SHAP can sometimes return a list depending on the model
    # configuration. For binary classification, use the
    # positive-class explanation when necessary.
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    reason_df = pd.DataFrame({
        "feature": processed_input.columns,
        "shap_value": shap_values[0],
        "feature_value": processed_input.iloc[0].values
    })

    # Only consider features contributing toward increased
    # failure risk.
    risk_reasons = reason_df[
        reason_df["shap_value"] > 0
    ].copy()

    risk_reasons["abs_shap"] = risk_reasons["shap_value"].abs()

    top_reasons = (
        risk_reasons
        .sort_values("abs_shap", ascending=False)
        ["feature"]
        .head(5)
        .tolist()
    )

    # Fallback if SHAP does not find positive contributors
    if len(top_reasons) == 0:
        top_reasons = ["General academic monitoring"]

    # --------------------------------------------------------
    # Intervention recommendations
    # --------------------------------------------------------

    interventions = generate_intervention_plan(
        student_dict,
        top_reasons
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "risk_probability": round(float(risk_probability), 3),
        "threshold": float(threshold),
        "prediction": (
            "At Risk"
            if prediction == 1
            else "Not At Risk"
        ),
        "top_reasons": top_reasons,
        "intervention_plan": interventions
    }


# ============================================================
# CSV PREDICTION
# ============================================================

@app.post("/predict-csv")
def predict_csv(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    probabilities = model.predict_proba(df)[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    results = df.copy()

    results["risk_probability"] = probabilities

    results["predicted_fail_risk"] = predictions

    results["risk_label"] = results[
        "predicted_fail_risk"
    ].map({
        0: "Not At Risk",
        1: "At Risk"
    })

    # --------------------------------------------------------
    # Generate reasons + interventions
    # --------------------------------------------------------

    top_reasons_list = []
    intervention_list = []

    for _, row in df.iterrows():

        student_dict = row.to_dict()

        top_reasons = []

        if student_dict.get("failures", 0) > 0:
            top_reasons.append("Past failures")

        if student_dict.get("absences", 0) > 10:
            top_reasons.append("High absences")

        if student_dict.get("studytime", 0) <= 2:
            top_reasons.append("Low study time")

        if student_dict.get("goout", 0) >= 4:
            top_reasons.append(
                "High social/outgoing time"
            )

        if student_dict.get("health", 5) <= 2:
            top_reasons.append(
                "Low health score"
            )

        if len(top_reasons) == 0:
            top_reasons.append(
                "General academic monitoring"
            )

        interventions = generate_intervention_plan(
            student_dict,
            top_reasons
        )

        top_reasons_list.append(
            ", ".join(top_reasons)
        )

        intervention_list.append(
            " | ".join(interventions)
        )

    results["top_reasons"] = top_reasons_list

    results["intervention_plan"] = intervention_list

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "total_students": len(results),

        "at_risk_students": int(
            results["predicted_fail_risk"].sum()
        ),

        "not_at_risk_students": int(
            (results["predicted_fail_risk"] == 0).sum()
        ),

        "students": results.to_dict(
            orient="records"
        )
    }


# ============================================================
# CSV PREDICTION + DOWNLOAD
# ============================================================

@app.post("/predict-csv-download")
def predict_csv_download(
    file: UploadFile = File(...)
):

    df = pd.read_csv(file.file)

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    probabilities = model.predict_proba(df)[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    results = df.copy()

    results["risk_probability"] = probabilities

    results["predicted_fail_risk"] = predictions

    results["risk_label"] = results[
        "predicted_fail_risk"
    ].map({
        0: "Not At Risk",
        1: "At Risk"
    })

    # --------------------------------------------------------
    # Generate reasons + interventions
    # --------------------------------------------------------

    top_reasons_list = []
    intervention_list = []

    for _, row in df.iterrows():

        student_dict = row.to_dict()

        top_reasons = []

        if student_dict.get("failures", 0) > 0:
            top_reasons.append("Past failures")

        if student_dict.get("absences", 0) > 10:
            top_reasons.append("High absences")

        if student_dict.get("studytime", 0) <= 2:
            top_reasons.append("Low study time")

        if student_dict.get("goout", 0) >= 4:
            top_reasons.append(
                "High social/outgoing time"
            )

        if student_dict.get("health", 5) <= 2:
            top_reasons.append(
                "Low health score"
            )

        if len(top_reasons) == 0:
            top_reasons.append(
                "General academic monitoring"
            )

        interventions = generate_intervention_plan(
            student_dict,
            top_reasons
        )

        top_reasons_list.append(
            ", ".join(top_reasons)
        )

        intervention_list.append(
            " | ".join(interventions)
        )

    results["top_reasons"] = top_reasons_list

    results["intervention_plan"] = intervention_list

    # --------------------------------------------------------
    # Convert dataframe to CSV
    # --------------------------------------------------------

    stream = io.StringIO()

    results.to_csv(
        stream,
        index=False
    )

    stream.seek(0)

    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )

    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=failsafe_predictions.csv"
    )

    return response
