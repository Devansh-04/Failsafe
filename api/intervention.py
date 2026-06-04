def generate_intervention_plan(student_data, top_reasons):
    interventions = []

    if "absences" in top_reasons or student_data.get("absences", 0) > 10:
        interventions.append("Monitor attendance and contact the student if absences continue.")

    if "studytime" in top_reasons or student_data.get("studytime", 0) <= 2:
        interventions.append("Create a weekly study schedule and recommend extra study sessions.")

    if "failures" in top_reasons or student_data.get("failures", 0) > 0:
        interventions.append("Assign academic mentoring because the student has past failures.")

    if "goout" in top_reasons or student_data.get("goout", 0) >= 4:
        interventions.append("Discuss time management and reduce non-academic distractions.")

    if "health" in top_reasons and student_data.get("health", 5) <= 2:
        interventions.append("Recommend counselling or health support if needed.")

    if len(interventions) == 0:
        interventions.append("Schedule a faculty check-in and monitor performance in the next assessment.")

    return interventions