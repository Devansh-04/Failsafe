# 🛡️ FailSafe


## Student Risk Prediction & Intervention System

**FailSafe** is a machine learning powered web application that predicts whether a student is at academic risk and recommends suitable intervention strategies.

It combines **Machine Learning**, **FastAPI**, **React**, **PostgreSQL**, and **JWT Authentication** to create a complete end-to-end full stack ML project.

</div>

---

##  Project Overview

Many students struggle academically due to low attendance, poor study consistency, lack of sleep, incomplete assignments, or weak previous performance.

**FailSafe** helps identify such students early by analyzing important academic and behavioral factors. Based on the predicted risk level, the system also suggests suitable intervention actions.

This project is designed as a practical academic analytics system that can be useful for:

* Student performance monitoring
* Early academic risk detection
* Personalized intervention planning
* Educational data analysis
* ML-based decision support

---

##  Features

*  User registration and login
*  JWT-based authentication
*  Machine learning based student risk prediction
*  Risk probability calculation
*  High Risk / Low Risk classification
*  Personalized intervention recommendation
*  PostgreSQL database integration
*  Prediction history for each user
*  FastAPI backend
*  React frontend
*  Clean project structure
*  Full stack ML deployment-ready architecture

---

##  Machine Learning Model

The ML model predicts student academic risk using factors such as:

* Study hours
* Attendance percentage
* Previous academic score
* Sleep hours
* Assignment completion percentage

The model returns:

* Risk probability
* Risk status
* Recommended intervention

Example output:

```json
{
  "risk_probability": 0.82,
  "risk_status": "High Risk",
  "intervention": "Moderate intervention needed: improve study consistency, assignment completion, and regular faculty feedback."
}
```

---

##  Tech Stack

### Frontend

* React
* JavaScript
* HTML
* CSS
* Vite

### Backend

* FastAPI
* Python
* Uvicorn
* Pydantic
* SQLAlchemy

### Machine Learning

* Scikit-learn
* Pandas
* NumPy
* Joblib

### Database

* PostgreSQL

### Authentication

* JWT
* Passlib
* Bcrypt
* Python-JOSE

---

##  Project Structure

```txt
FAILSAFE/
│
├── api/
│   ├── auth.py
│   ├── database.py
│   ├── intervention.py
│   ├── main.py
│   └── schemas.py
│
├── data/
│   ├── processed/
│   └── raw/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── models/
│   ├── failsafe_feature_names.pkl
│   ├── failsafe_model.pkl
│   └── failsafe_threshold.pkl
│
├── notebooks/
│   └── failsafe_ml.ipynb
│
├── reports/
│
├── test_students.csv
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

---

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

---

## 1. Clone the Repository

```bash
git clone https://github.com/Devansh-04/Failsafe.git
cd Failsafe
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

## 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create PostgreSQL Database

Open PostgreSQL or pgAdmin and create a database:

```sql
CREATE DATABASE failsafe_db;
```

---

## 5. Create `.env` File

Create a `.env` file in the root folder:

```txt
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/failsafe_db
SECRET_KEY=this_is_my_failsafe_secret_key_change_later
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Replace `your_password` with your actual PostgreSQL password.

---

## 6. Run the Backend

From the root folder, run:

```bash
uvicorn api.main:app --reload
```

The backend will start at:

```txt
http://127.0.0.1:8000
```

FastAPI documentation will be available at:

```txt
http://127.0.0.1:8000/docs
```

---

## 7. Setup Frontend

Open a new terminal and go to the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at:

```txt
http://localhost:5173
```

---

##  Authentication Flow

FailSafe uses JWT authentication.

The user must first register and then login.

After successful login, a JWT token is generated and stored in local storage. This token is then used to access protected routes such as:

* `/predict`
* `/history`

---

##  API Endpoints

### Home Route

```http
GET /
```

Checks if the API is running.

---

### Register User

```http
POST /register
```

Request body:

```json
{
  "username": "devansh",
  "password": "password123"
}
```

Response:

```json
{
  "message": "User registered successfully"
}
```

---

### Login User

```http
POST /login
```

Request body:

```json
{
  "username": "devansh",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

---

### Predict Student Risk

```http
POST /predict
```

Protected route. Requires JWT token.

Request body:

```json
{
  "study_hours": 4,
  "attendance": 72,
  "previous_score": 65,
  "sleep_hours": 6,
  "assignment_completion": 70
}
```

Response:

```json
{
  "risk_probability": 0.78,
  "risk_status": "High Risk",
  "intervention": "Moderate intervention needed: improve study consistency, assignment completion, and regular faculty feedback."
}
```

---

### Get Prediction History

```http
GET /history
```

Protected route. Requires JWT token.

Returns all previous predictions made by the logged-in user.

---

##  Frontend Pages

The React frontend contains:

* Login form
* Registration form
* Student risk prediction form
* Prediction result section
* Intervention recommendation section
* Prediction history section
* Logout button

---

##  Sample Input

```txt
Study Hours: 4
Attendance: 72
Previous Score: 65
Sleep Hours: 6
Assignment Completion: 70
```

---

##  Sample Output

```txt
Risk Probability: 78.00%
Risk Status: High Risk
Recommended Intervention:
Moderate intervention needed: improve study consistency, assignment completion, and regular faculty feedback.
```

---

##  How FailSafe Works

```txt
User registers/logs in
        ↓
JWT token is generated
        ↓
User enters student data
        ↓
Frontend sends data to FastAPI backend
        ↓
Backend loads trained ML model
        ↓
Model predicts risk probability
        ↓
Risk status is calculated using threshold
        ↓
Intervention is generated
        ↓
Prediction is saved in PostgreSQL
        ↓
Result is shown on frontend
```

---

##  Database Tables

The project uses PostgreSQL with two main tables.

### Users Table

Stores registered users.

```txt
id
username
password_hash
```

### Prediction History Table

Stores prediction records of each user.

```txt
id
user_id
study_hours
attendance
previous_score
sleep_hours
assignment_completion
risk_probability
risk_status
intervention
created_at
```

---

##  Testing the API

You can test the backend using FastAPI Swagger UI:

```txt
http://127.0.0.1:8000/docs
```

Recommended testing order:

```txt
1. /register
2. /login
3. Authorize using Bearer token
4. /predict
5. /history
```

For protected routes, use:

```txt
Bearer your_token_here
```

---

##  Important Files

### `api/main.py`

Main FastAPI application. It handles:

* API routes
* ML model loading
* Prediction logic
* Database saving
* Authentication protected routes

### `api/auth.py`

Handles:

* Password hashing
* Password verification
* JWT token creation
* Current user authentication

### `api/database.py`

Handles:

* PostgreSQL connection
* SQLAlchemy models
* Database session creation

### `api/intervention.py`

Contains logic for intervention recommendation based on risk status and probability.

### `models/failsafe_model.pkl`

Trained machine learning model.

### `models/failsafe_feature_names.pkl`

Stores the feature names used during model training.

### `models/failsafe_threshold.pkl`

Stores the custom threshold used for risk classification.

### `frontend/src/App.jsx`

Main React frontend file.

---

##  Key Highlights

* End-to-end ML project
* Full stack architecture
* Real authentication system
* PostgreSQL database integration
* Prediction history tracking
* Clean API design
* Practical educational use case
* Resume-friendly project
* Easy to extend and deploy

---

##  Future Improvements

Some possible future improvements are:

* Admin dashboard for monitoring multiple students
* Graphs and visual analytics
* CSV upload for batch prediction
* Role-based authentication
* Email alerts for high-risk students
* Improved UI with charts
* Deployment on Render, Railway, Vercel, or Supabase
* More advanced ML models
* Explainable AI using SHAP

---

##  License

Released under the [MIT License](LICENSE).

---

## 🧑‍💻 Author

**Devansh Singh**

[![GitHub](https://img.shields.io/badge/GitHub-Devansh--04-181717?logo=github&logoColor=white)](https://github.com/Devansh-04)

---

## ⭐ Conclusion

FailSafe is an end-to-end machine learning based academic risk prediction system that combines data science, backend development, frontend development, authentication, and database management.

It demonstrates how machine learning can be integrated into a real-world full stack application to support early student risk detection and intervention planning.

---
