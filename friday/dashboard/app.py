import streamlit as st
from friday.intelligence.strategy import get_best_stock
from friday.learning.dashboard import dashboard
from friday.memory.cleaner import cleanup
from friday.autonomous.scanner import scan_events

st.title("🛠️ FRIDAY Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.header("🧠 Intelligence")
    best = get_best_stock()
    st.metric("Best Stock", best['symbol'], best['combined_conf'])
    st.write(best['top3'])

with col2:
    st.header("📊 Learning")
    dashboard()

st.header("🚨 Autonomous Alerts")
events = scan_events()
for event in events:
    st.warning(f"{event['symbol']}: Vol spike/drop")

if st.button("🧹 Clean Memory"):
    cleanup()
    st.success("Memory cleaned.")

st.header("Start Voice Agent")
if st.button("🎤 Listen"):
    from friday.core.agent import StarkAgent
    agent = StarkAgent()
    agent.run_voice_loop()

