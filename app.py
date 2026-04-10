import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Springfield Wrestling",
    page_icon="🤼",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_roster():
    return pd.read_csv("data/roster.csv")

@st.cache_data
def load_matches():
    df = pd.read_csv("data/matches.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

roster  = load_roster()
matches = load_matches()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤼 Springfield Wrestling")
    st.caption("Coach Dashboard · 2024–25")
    st.divider()
    page = st.radio(
        "Navigate",
        ["📊 Team Overview", "👤 Roster", "🏆 Match Results", "📅 Training Plan"],
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — TEAM OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "📊 Team Overview":

    st.title("📊 Team Overview")
    st.caption("Springfield Wrestling · 2024–25 Season")
    st.divider()

    # ── Metrics ──────────────────────────────────────────────────────────────
    wins   = (matches["result"] == "Win").sum()
    losses = (matches["result"] == "Loss").sum()
    draws  = (matches["result"] == "Draw").sum()
    total  = wins + losses + draws
    win_pct = round(wins / total * 100) if total > 0 else 0
    active  = len(roster[roster["status"] == "Active"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Team Wins",        wins)
    c2.metric("Team Losses",      losses)
    c3.metric("Win Rate",         f"{win_pct}%")
    c4.metric("Active Wrestlers", active)
    c5.metric("Meets Played",     total)

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Results by Meet")
        fig = px.bar(
            matches,
            x="opponent",
            y=["team_score", "opponent_score"],
            barmode="group",
            labels={"value": "Score", "opponent": "Opponent", "variable": ""},
            color_discrete_map={
                "team_score":     "#1D9E75",
                "opponent_score": "#E24B4A",
            },
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=0, r=0, t=8, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Win / Loss / Draw")
        pie_data = pd.DataFrame({
            "Result": ["Win", "Loss", "Draw"],
            "Count":  [wins, losses, draws],
        })
        fig2 = px.pie(
            pie_data,
            values="Count",
            names="Result",
            color="Result",
            color_discrete_map={
                "Win":  "#1D9E75",
                "Loss": "#E24B4A",
                "Draw": "#BA7517",
            },
            hole=0.5,
        )
        fig2.update_layout(
            paper_bgcolor="white",
            margin=dict(l=0, r=0, t=8, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Roster win-rate bar ───────────────────────────────────────────────────
    st.divider()
    st.subheader("Individual Win Rate — All Wrestlers")

    roster_sorted = roster.copy()
    roster_sorted["win_pct"] = (
        roster_sorted["wins"] / (roster_sorted["wins"] + roster_sorted["losses"]) * 100
    ).round(1)
    roster_sorted = roster_sorted.sort_values("win_pct", ascending=True)

    colors = [
        "#1D9E75" if p >= 60 else "#BA7517" if p >= 40 else "#E24B4A"
        for p in roster_sorted["win_pct"]
    ]

    fig3 = go.Figure(go.Bar(
        x=roster_sorted["win_pct"],
        y=roster_sorted["name"],
        orientation="h",
        marker_color=colors,
        text=[f"{p}%" for p in roster_sorted["win_pct"]],
        textposition="outside",
    ))
    fig3.update_layout(
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 115], showticklabels=False, showgrid=False),
        margin=dict(l=0, r=60, t=8, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ROSTER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👤 Roster":

    st.title("👤 Roster")
    st.caption("Springfield Wrestling · 2024–25 Athletes")
    st.divider()

    # Filters
    col1, col2 = st.columns([2, 2])
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["Active", "Watch"],
            default=["Active", "Watch"],
        )
    with col2:
        search = st.text_input("Search by name", placeholder="Type a name...")

    filtered = roster[roster["status"].isin(status_filter)] if status_filter else roster
    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False)]

    st.divider()

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wrestlers", len(filtered))
    c2.metric("Total Wins",   int(filtered["wins"].sum()))
    c3.metric("Total Losses", int(filtered["losses"].sum()))
    c4.metric("Avg Win Rate",
              f"{(filtered['wins'] / (filtered['wins'] + filtered['losses']) * 100).mean():.1f}%")

    st.divider()

    # Table
    display = filtered.copy()
    display["win_pct"] = (
        display["wins"] / (display["wins"] + display["losses"]) * 100
    ).round(1)
    display = display[["name", "weight_class", "wins", "losses", "win_pct", "status"]]
    display.columns = ["Name", "Weight Class", "Wins", "Losses", "Win %", "Status"]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Win %": st.column_config.ProgressColumn(
                "Win %", min_value=0, max_value=100, format="%.1f%%"
            ),
        },
    )

    # Wrestler detail
    st.divider()
    st.subheader("Wrestler Detail")
    selected = st.selectbox("Select a wrestler", filtered["name"].tolist())
    if selected:
        w = filtered[filtered["name"] == selected].iloc[0]
        wp = round(w["wins"] / (w["wins"] + w["losses"]) * 100, 1)
        ca, cb, cc = st.columns(3)
        ca.metric("Record",   f"{w['wins']}W – {w['losses']}L")
        cb.metric("Win Rate", f"{wp}%")
        cc.metric("Status",   w["status"])


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MATCH RESULTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Match Results":

    st.title("🏆 Match Results")
    st.caption("Springfield Wrestling · Dual Meet History")
    st.divider()

    # Result cards
    for _, row in matches.sort_values("date", ascending=False).iterrows():
        color = (
            "#1D9E75" if row["result"] == "Win"
            else "#E24B4A" if row["result"] == "Loss"
            else "#BA7517"
        )
        loc_icon = "🏠" if row["location"] == "Home" else "✈️"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:14px 20px;border-radius:10px;border:1px solid #ebebeb;
                        margin-bottom:8px;">
                <div>
                    <span style="font-size:18px;font-weight:700;color:{color};">
                        {row['result'].upper()}
                    </span>
                    &nbsp;&nbsp;
                    <span style="font-size:15px;font-weight:500;">vs {row['opponent']}</span>
                    <br/>
                    <span style="font-size:12px;color:#888;">
                        {row['date'].strftime('%b %d, %Y')} · {loc_icon} {row['location']}
                    </span>
                </div>
                <div style="font-size:28px;font-weight:700;letter-spacing:2px;">
                    {row['team_score']}
                    <span style="color:#ccc;">–</span>
                    {row['opponent_score']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Season trend line
    st.subheader("Score Trend — Season")
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(
        x=matches["date"], y=matches["team_score"],
        name="Springfield", mode="lines+markers",
        line=dict(color="#1D9E75", width=2),
        marker=dict(size=7),
    ))
    fig_t.add_trace(go.Scatter(
        x=matches["date"], y=matches["opponent_score"],
        name="Opponent", mode="lines+markers",
        line=dict(color="#E24B4A", width=2, dash="dot"),
        marker=dict(size=7),
    ))
    fig_t.update_layout(
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_t, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TRAINING PLAN
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📅 Training Plan":

    st.title("📅 Training Plan")
    st.caption("Springfield Wrestling · Weekly Schedule")
    st.divider()

    # ── This week's plan (static starter — editable below) ───────────────────
    st.subheader("This Week")

    weekly = pd.DataFrame([
        {"Day": "Monday",    "Type": "Technical",   "Focus": "Takedowns",        "Intensity": "Medium", "Duration": "90 min"},
        {"Day": "Tuesday",   "Type": "Strength",    "Focus": "Weight Room",      "Intensity": "High",   "Duration": "75 min"},
        {"Day": "Wednesday", "Type": "Sparring",    "Focus": "Live Wrestling",   "Intensity": "High",   "Duration": "90 min"},
        {"Day": "Thursday",  "Type": "Recovery",    "Focus": "Flexibility",      "Intensity": "Low",    "Duration": "60 min"},
        {"Day": "Friday",    "Type": "Technical",   "Focus": "Top & Bottom",     "Intensity": "Medium", "Duration": "90 min"},
        {"Day": "Saturday",  "Type": "Scrimmage",   "Focus": "Match Simulation", "Intensity": "High",   "Duration": "120 min"},
        {"Day": "Sunday",    "Type": "Rest",        "Focus": "Off",              "Intensity": "—",      "Duration": "—"},
    ])

    intensity_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "—": "⚪"}
    weekly["Intensity"] = weekly["Intensity"].map(
        lambda x: f"{intensity_color.get(x, '')} {x}"
    )

    st.dataframe(weekly, use_container_width=True, hide_index=True)

    st.divider()

    # ── Add a session form ────────────────────────────────────────────────────
    st.subheader("Add a Session Note")

    with st.form("session_form"):
        f1, f2, f3 = st.columns(3)
        with f1:
            s_day  = st.selectbox("Day", ["Monday","Tuesday","Wednesday",
                                          "Thursday","Friday","Saturday","Sunday"])
            s_type = st.selectbox("Session Type",
                                  ["Technical","Strength","Sparring",
                                   "Recovery","Scrimmage","Competition","Rest"])
        with f2:
            s_int  = st.selectbox("Intensity", ["High", "Medium", "Low"])
            s_dur  = st.number_input("Duration (min)", 0, 240, 90, step=15)
        with f3:
            s_focus = st.text_input("Focus Area", placeholder="e.g. Takedowns")
            s_notes = st.text_input("Notes",      placeholder="Optional notes")

        submitted = st.form_submit_button("Save Session", use_container_width=True)
        if submitted:
            st.success(
                f"✅ Saved: **{s_type}** on **{s_day}** · {s_int} intensity · {s_dur} min"
                + (f" · {s_focus}" if s_focus else "")
            )

    st.divider()
    st.info("💡 Tip: To make sessions persist permanently, add rows directly to data/training_schedule.csv in GitHub.")
