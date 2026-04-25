import streamlit as st
from datetime import date
from database import insert_data
from analytics import get_data, consistency_score, calculate_streak, generate_insights, detect_patterns, generate_recommendations, productivity_prediction
from ai_engine import generate_ai_coaching
import altair as alt

# Page config for a wider, cleaner layout
st.set_page_config(page_title="AI Habit Tracker", page_icon="✨", layout="wide")

st.title("✨ AI Habit Tracker")
st.markdown("---")

today = date.today()

# Split data entry into two clean columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Daily Actions")
    coding = st.checkbox("💻 Did you code today?")
    exercise = st.checkbox("🏃‍♂️ Did you exercise today?")
    reading = st.checkbox("📚 Did you read today?")

with col2:
    st.subheader("Time Metrics")
    study_hours = st.slider("Study hours", 0.0, 10.0, 2.0, step=0.5)
    sleep_hours = st.slider("Sleep hours", 0.0, 12.0, 7.0, step=0.5)

if st.button("Save Today's Data", type="primary"):
    # Save date as a formatted string to avoid SQLite type issues
    insert_data(today.strftime("%Y-%m-%d"), int(coding), int(exercise), int(reading), study_hours, sleep_hours)
    st.success("Data saved successfully! Great job showing up today.")

st.markdown("---")
st.header("📊 Your Progress Dashboard")

df = get_data()

if not df.empty:
    score = consistency_score(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Consistency Score", f"{score}%")
    m2.metric("Coding Streak", f"{calculate_streak(df, 'coding')} days 🔥")
    m3.metric("Exercise Streak", f"{calculate_streak(df, 'exercise')} days 💪")
    m4.metric("Reading Streak", f"{calculate_streak(df, 'reading')} days 📚")

    st.subheader("Habit Distribution")

    # 1. Format the data for Altair
    habit_counts = df[["reading", "coding", "exercise"]].sum().reset_index()
    habit_counts.columns = ["Habit", "Days Logged"]

    # 2. Create a static chart (no zoom/scroll hijacking)
    chart = alt.Chart(habit_counts).mark_bar(color="#d4af37").encode(
        x=alt.X("Habit", axis=alt.Axis(labelAngle=0)), 
        y=alt.Y("Days Logged", axis=alt.Axis(tickMinStep=1))
    )

    # 3. Render it
    st.altair_chart(chart, width="stretch")

    # AI Section inside an expander to keep the main view clean
    with st.expander("🤖 AI Coaching & Insights", expanded=True):
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            st.subheader("Smart Insights")
            for insight in generate_insights(df):
                st.write(f"• {insight}")
                
            st.subheader("Behavior Patterns")
            for pattern in detect_patterns(df):
                st.write(f"• {pattern}")

        with ai_col2:
            st.subheader("Productivity Forecast")
            st.info(productivity_prediction(df))
            
            st.subheader("AI Coach")
            with st.spinner("Analyzing your data..."):
                try:
                    st.success(generate_ai_coaching(df))
                except Exception as e:
                    st.warning(f"AI coaching temporarily unavailable. Ensure API key is correct.")
else:
    st.info("No data available yet. Start tracking above to unlock your dashboard!")