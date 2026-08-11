import { useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [singlePrediction, setSinglePrediction] = useState(null);

  const [studentForm, setStudentForm] = useState({
    school: "GP",
    sex: "F",
    age: 17,
    address: "U",
    famsize: "GT3",
    Pstatus: "T",
    Medu: 2,
    Fedu: 2,
    Mjob: "at_home",
    Fjob: "other",
    reason: "course",
    guardian: "mother",
    traveltime: 2,
    studytime: 1,
    failures: 1,
    schoolsup: "yes",
    famsup: "yes",
    paid: "no",
    activities: "no",
    nursery: "yes",
    higher: "yes",
    internet: "yes",
    romantic: "no",
    famrel: 3,
    freetime: 4,
    goout: 4,
    Dalc: 2,
    Walc: 3,
    health: 3,
    absences: 15,
  });

  const handleFileUpload = async () => {
    if (!file) {
      alert("Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await axios.post(`${API_BASE}/predict-csv`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSummary({
        total_students: response.data.total_students,
        at_risk_students: response.data.at_risk_students,
        not_at_risk_students: response.data.not_at_risk_students,
      });

      setStudents(response.data.students);
    } catch (error) {
      console.error(error);
      alert("Error while predicting CSV. Check FastAPI server.");
    } finally {
      setLoading(false);
    }
  };

  const downloadPredictions = async () => {
    if (!file) {
      alert("Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `${API_BASE}/predict-csv-download`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "failsafe_predictions.csv");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error(error);
      alert("Error while downloading predictions.");
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;

    const numericFields = [
      "age",
      "Medu",
      "Fedu",
      "traveltime",
      "studytime",
      "failures",
      "famrel",
      "freetime",
      "goout",
      "Dalc",
      "Walc",
      "health",
      "absences",
    ];

    setStudentForm({
      ...studentForm,
      [name]: numericFields.includes(name) ? Number(value) : value,
    });
  };

  const predictSingleStudent = async () => {
    try {
      const response = await axios.post(`${API_BASE}/predict`, studentForm);
      setSinglePrediction(response.data);
    } catch (error) {
      console.error(error);
      alert("Error while predicting single student. Check FastAPI server.");
    }
  };

  const chartData = summary
    ? [
        { name: "At Risk", value: summary.at_risk_students },
        { name: "Not At Risk", value: summary.not_at_risk_students },
      ]
    : [];

  const topRiskStudents = [...students]
    .sort((a, b) => b.risk_probability - a.risk_probability)
    .slice(0, 10);

  const highRiskStudents = [...students]
    .filter((student) => student.risk_label === "At Risk")
    .sort((a, b) => b.risk_probability - a.risk_probability)
    .slice(0, 5);

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>FAILSAFE</h1>
          <p>Early student failure-risk prediction dashboard</p>
        </div>
        <span className="badge">XGBoost + React + FastAPI</span>
      </header>

      <section className="upload-card">
        <h2>Upload Student CSV</h2>
        <p>
          Upload a CSV containing student attendance, academic background, and
          behavioural features.
        </p>

        <div className="upload-row">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button onClick={handleFileUpload} disabled={loading}>
            {loading ? "Predicting..." : "Predict Risk"}
          </button>

          <button className="secondary-btn" onClick={downloadPredictions}>
            Download CSV
          </button>
        </div>
      </section>

      <section className="upload-card">
        <h2>Single Student Prediction</h2>
        <p>
          Enter one student's details to get individual failure-risk prediction,
          reasons, and intervention plan.
        </p>

        <div className="form-grid">
          <input
            name="age"
            type="number"
            value={studentForm.age}
            onChange={handleFormChange}
            placeholder="Age"
          />

          <input
            name="studytime"
            type="number"
            value={studentForm.studytime}
            onChange={handleFormChange}
            placeholder="Study Time"
          />

          <input
            name="failures"
            type="number"
            value={studentForm.failures}
            onChange={handleFormChange}
            placeholder="Failures"
          />

          <input
            name="absences"
            type="number"
            value={studentForm.absences}
            onChange={handleFormChange}
            placeholder="Absences"
          />

          <input
            name="goout"
            type="number"
            value={studentForm.goout}
            onChange={handleFormChange}
            placeholder="Go Out"
          />

          <input
            name="health"
            type="number"
            value={studentForm.health}
            onChange={handleFormChange}
            placeholder="Health"
          />
        </div>

        <button onClick={predictSingleStudent}>Predict Single Student</button>

        {singlePrediction && (
          <div className="single-result">
            <h3>Prediction Result</h3>

            <p>
              <strong>Risk Probability:</strong>{" "}
              {Number(singlePrediction.risk_probability).toFixed(3)}
            </p>

            <p>
              <strong>Prediction:</strong>{" "}
              <span
                className={
                  singlePrediction.prediction === "At Risk"
                    ? "risk-label danger-label"
                    : "risk-label safe-label"
                }
              >
                {singlePrediction.prediction}
              </span>
            </p>

            <p>
              <strong>Top Reasons:</strong>{" "}
              {singlePrediction.top_reasons.join(", ")}
            </p>

            <p>
              <strong>Intervention Plan:</strong>{" "}
              {singlePrediction.intervention_plan.join(" | ")}
            </p>
          </div>
        )}
      </section>

      {summary && (
        <>
          <section className="stats-grid">
            <div className="stat-card">
              <p>Total Students</p>
              <h2>{summary.total_students}</h2>
            </div>

            <div className="stat-card danger">
              <p>At Risk</p>
              <h2>{summary.at_risk_students}</h2>
            </div>

            <div className="stat-card safe">
              <p>Not At Risk</p>
              <h2>{summary.not_at_risk_students}</h2>
            </div>
          </section>

          <section className="charts-grid">
            <div className="chart-card">
              <h2>Risk Distribution</h2>

              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={90}
                    label
                  >
                    {chartData.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={index === 0 ? "#ef4444" : "#22c55e"}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h2>Top Risk Students</h2>

              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={topRiskStudents}>
                  <XAxis dataKey="age" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="risk_probability" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="table-card priority-card">
            <h2>High-Risk Priority Students</h2>
            <p className="section-desc">
              These students should be reviewed first by faculty or mentors.
            </p>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Priority</th>
                    <th>Age</th>
                    <th>Study Time</th>
                    <th>Failures</th>
                    <th>Absences</th>
                    <th>Risk Probability</th>
                    <th>Top Reasons</th>
                    <th>Suggested Intervention</th>
                  </tr>
                </thead>

                <tbody>
                  {highRiskStudents.map((student, index) => (
                    <tr key={index}>
                      <td>#{index + 1}</td>
                      <td>{student.age}</td>
                      <td>{student.studytime}</td>
                      <td>{student.failures}</td>
                      <td>{student.absences}</td>
                      <td>{Number(student.risk_probability).toFixed(3)}</td>
                      <td>{student.top_reasons}</td>
                      <td>{student.intervention_plan}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="table-card">
            <h2>Student Risk Table</h2>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Age</th>
                    <th>Study Time</th>
                    <th>Failures</th>
                    <th>Absences</th>
                    <th>Risk Probability</th>
                    <th>Risk Label</th>
                    <th>Top Reasons</th>
                    <th>Intervention Plan</th>
                  </tr>
                </thead>

                <tbody>
                  {students.map((student, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>{student.age}</td>
                      <td>{student.studytime}</td>
                      <td>{student.failures}</td>
                      <td>{student.absences}</td>
                      <td>{Number(student.risk_probability).toFixed(3)}</td>
                      <td>
                        <span
                          className={
                            student.risk_label === "At Risk"
                              ? "risk-label danger-label"
                              : "risk-label safe-label"
                          }
                        >
                          {student.risk_label}
                        </span>
                      </td>
                      <td>{student.top_reasons}</td>
                      <td>{student.intervention_plan}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export default App;