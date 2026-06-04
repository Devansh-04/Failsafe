import joblib
import pandas as pd
import shap
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from schemas import StudentInput
from intervention import generate_intervention_plan
from fastapi.middleware.cors import CORSMiddleware
import io


app = FastAPI(
    title="FAILSAFE API",
    description="Student failure-risk prediction API using XGBoost and SHAP",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = joblib.load("../models/failsafe_model.pkl")
threshold = joblib.load("../models/failsafe_threshold.pkl")


@app.get("/")
def home():
    return {
        "message": "FAILSAFE API is running",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/predict")
def predict_student_risk(student: StudentInput):
    student_dict = student.dict()

    input_df = pd.DataFrame([student_dict])

    risk_probability = model.predict_proba(input_df)[0][1]
    prediction = int(risk_probability >= threshold)

    preprocessor = model.named_steps["preprocessor"]
    xgb_model = model.named_steps["model"]

    cat_cols = input_df.select_dtypes(include=["object"]).columns.tolist()
    num_cols = input_df.select_dtypes(exclude=["object"]).columns.tolist()

    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols)
    all_feature_names = list(cat_feature_names) + num_cols

    processed_input = preprocessor.transform(input_df)
    processed_input = pd.DataFrame(processed_input, columns=all_feature_names)

    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(processed_input)

    reason_df = pd.DataFrame({
        "feature": processed_input.columns,
        "shap_value": shap_values[0],
        "feature_value": processed_input.iloc[0].values
    })

    risk_reasons = reason_df[reason_df["shap_value"] > 0].copy()
    risk_reasons["abs_shap"] = risk_reasons["shap_value"].abs()

    top_reasons = risk_reasons.sort_values("abs_shap", ascending=False)["feature"].head(5).tolist()

    interventions = generate_intervention_plan(student_dict, top_reasons)

    return {
        "risk_probability": round(float(risk_probability), 3),
        "threshold": float(threshold),
        "prediction": "At Risk" if prediction == 1 else "Not At Risk",
        "top_reasons": top_reasons,
        "intervention_plan": interventions
    }

@app.post("/predict-csv")
def predict_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    probabilities = model.predict_proba(df)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    results = df.copy()
    results["risk_probability"] = probabilities
    results["predicted_fail_risk"] = predictions
    results["risk_label"] = results["predicted_fail_risk"].map({
        0: "Not At Risk",
        1: "At Risk"
    })

    top_reasons_list = []
    intervention_list = []

    for index, row in df.iterrows():
        student_dict = row.to_dict()

        top_reasons = []

        if student_dict.get("failures", 0) > 0:
            top_reasons.append("Past failures")

        if student_dict.get("absences", 0) > 10:
            top_reasons.append("High absences")

        if student_dict.get("studytime", 0) <= 2:
            top_reasons.append("Low study time")

        if student_dict.get("goout", 0) >= 4:
            top_reasons.append("High social/outgoing time")

        if student_dict.get("health", 5) <= 2:
            top_reasons.append("Low health score")

        if len(top_reasons) == 0:
            top_reasons.append("General academic monitoring")

        interventions = generate_intervention_plan(student_dict, top_reasons)

        top_reasons_list.append(", ".join(top_reasons))
        intervention_list.append(" | ".join(interventions))

    results["top_reasons"] = top_reasons_list
    results["intervention_plan"] = intervention_list

    return {
        "total_students": len(results),
        "at_risk_students": int(results["predicted_fail_risk"].sum()),
        "not_at_risk_students": int((results["predicted_fail_risk"] == 0).sum()),
        "students": results.to_dict(orient="records")
    }

@app.post("/predict-csv-download")
def predict_csv_download(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    probabilities = model.predict_proba(df)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    results = df.copy()
    results["risk_probability"] = probabilities
    results["predicted_fail_risk"] = predictions
    results["risk_label"] = results["predicted_fail_risk"].map({
        0: "Not At Risk",
        1: "At Risk"
    })

    top_reasons_list = []
    intervention_list = []

    for index, row in df.iterrows():
        student_dict = row.to_dict()

        top_reasons = []

        if student_dict.get("failures", 0) > 0:
            top_reasons.append("Past failures")

        if student_dict.get("absences", 0) > 10:
            top_reasons.append("High absences")

        if student_dict.get("studytime", 0) <= 2:
            top_reasons.append("Low study time")

        if student_dict.get("goout", 0) >= 4:
            top_reasons.append("High social/outgoing time")

        if student_dict.get("health", 5) <= 2:
            top_reasons.append("Low health score")

        if len(top_reasons) == 0:
            top_reasons.append("General academic monitoring")

        interventions = generate_intervention_plan(student_dict, top_reasons)

        top_reasons_list.append(", ".join(top_reasons))
        intervention_list.append(" | ".join(interventions))

    results["top_reasons"] = top_reasons_list
    results["intervention_plan"] = intervention_list

    stream = io.StringIO()
    results.to_csv(stream, index=False)
    stream.seek(0)

    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )

    response.headers["Content-Disposition"] = "attachment; filename=failsafe_predictions.csv"

    return response