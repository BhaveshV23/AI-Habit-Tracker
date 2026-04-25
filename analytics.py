import sqlite3
import pandas as pd

def get_data():
    conn = sqlite3.connect("data/habits.db")
    df = pd.read_sql_query("SELECT * FROM habits ORDER BY date", conn)

    return df

def consistency_score(df):
    if df.empty:
        return 0
    
    total_days = len(df)
    total_possible = total_days * 3
    completed = df[["coding", "exercise", "reading"]].sum().sum()
    score = (completed/total_possible)*100

    return round(score, 2)

def calculate_streak(df, habit):
    if df.empty or habit not in df.columns:
        return 0

    # Ensure dates are parsed and sorted correctly
    df["date"] = pd.to_datetime(df["date"])
    reversed_data = df.sort_values("date", ascending=False).reset_index(drop=True)

    streak = 0
    # Check if the last logged date was today or yesterday. 
    # If it was older, the active streak is dead.
    last_logged_date = reversed_data.iloc[0]["date"].date()
    today = pd.Timestamp('today').date()
    
    if (today - last_logged_date).days > 1:
        return 0
    
    for value in reversed_data[habit]:
        if value == 1:
            streak += 1
        else:
            break
    return streak

def generate_insights(df):

    if df.empty:
        return ["No data yet. Start tracking habits!"]

    insights = []

    habit_totals = df[["coding", "exercise", "reading"]].sum()

    best_habit = habit_totals.idxmax()
    worst_habit = habit_totals.idxmin()

    insights.append(f"Your strongest habit: {best_habit}")
    insights.append(f"Your weakest habit: {worst_habit}")

    avg_sleep = df["sleep_hours"].mean()

    if avg_sleep < 6:
        insights.append("You may not be getting enough sleep.")
    else:
        insights.append("Your sleep schedule looks healthy.")

    avg_study = df["study_hours"].mean()

    if avg_study < 2:
        insights.append("Try increasing study time slightly.")
    else:
        insights.append("Your study consistency looks strong.")

    return insights

def detect_patterns(df):

    if df.empty or len(df) < 3:
        return ["Not enough data yet to detect patterns."]

    insights = []

    df["date"] = pd.to_datetime(df["date"])
    df["weekday"] = df["date"].dt.weekday

    weekday_data = df[df["weekday"] < 5]
    weekend_data = df[df["weekday"] >= 5]

    weekday_coding = weekday_data["coding"].mean()
    weekend_coding = weekend_data["coding"].mean()

    if weekday_coding > weekend_coding:
        insights.append("You code more on weekdays than weekends.")
    else:
        insights.append("You code more on weekends than weekdays.")

    sleep_effect = df["sleep_hours"].corr(df["study_hours"])

    if df["sleep_hours"].nunique() > 1 and df["study_hours"].nunique() > 1:
        sleep_effect = df["sleep_hours"].corr(df["study_hours"])
        if pd.notna(sleep_effect):
            if sleep_effect > 0.3:
                insights.append("Better sleep correlates with more study hours.")
            elif sleep_effect < -0.3:
                insights.append("Sleep patterns are negatively impacting study hours.")
    else:
        insights.append("Sleep duration has been too consistent to find correlations.")

    return insights


def generate_recommendations(df):

    if df.empty:
        return ["Start tracking habits daily to receive recommendations."]

    recommendations = []

    habit_totals = df[["coding", "exercise", "reading"]].mean()

    if habit_totals["exercise"] < 0.4:
        recommendations.append("Try exercising at least 2–3 times per week.")

    if habit_totals["reading"] < 0.4:
        recommendations.append("Consider adding a short daily reading session.")

    if habit_totals["coding"] > 0.7:
        recommendations.append("Great coding consistency — maintain your streak!")

    avg_sleep = df["sleep_hours"].mean()

    if avg_sleep < 6:
        recommendations.append("Increase sleep slightly to improve productivity.")

    avg_study = df["study_hours"].mean()

    if avg_study < 2:
        recommendations.append("Increase study hours gradually by 30 minutes daily.")

    return recommendations


def productivity_prediction(df):

    if df.empty:
        return "Not enough data to predict productivity."

    latest = df.iloc[-1]

    score = 0

    if latest["coding"] == 1:
        score += 30

    if latest["study_hours"] >= 2:
        score += 30

    if latest["sleep_hours"] >= 6:
        score += 20

    streak_bonus = df["coding"].tail(3).sum()

    score += streak_bonus * 5

    if score >= 70:
        return "HIGH productivity expected tomorrow 🚀"

    elif score >= 40:
        return "MODERATE productivity expected tomorrow 👍"

    else:
        return "LOW productivity expected tomorrow ⚠️"