import streamlit as st
from supabase import create_client
import json
import time

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"

supabase = create_client(URL, KEY)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Cricket Scorer",
    layout="centered"
)

# -----------------------------
# DATABASE HELPERS
# -----------------------------
def get_match():
    res = (
        supabase.table("match_data")
        .select("*")
        .eq("id", 1)
        .single()
        .execute()
        .data
    )

    if "history" not in res or res["history"] is None:
        res["history"] = "[]"

    return res


def update_score(runs_inc, balls_inc, is_undo=False):

    d = get_match()
    history = json.loads(d["history"])

    # ---------------- UNDO ----------------
    if is_undo:

        if len(history) > 0:

            last = history.pop()

            new_runs = d["runs"] - last["r"]
            new_balls = d["balls"] - last["b"]

            supabase.table("match_data").update({
                "runs": max(0, new_runs),
                "balls": max(0, new_balls),
                "history": json.dumps(history)
            }).eq("id", 1).execute()

    # ---------------- NORMAL UPDATE ----------------
    else:

        history.append({
            "r": runs_inc,
            "b": balls_inc
        })

        if len(history) > 30:
            history.pop(0)

        supabase.table("match_data").update({
            "runs": d["runs"] + runs_inc,
            "balls": d["balls"] + balls_inc,
            "history": json.dumps(history)
        }).eq("id", 1).execute()


# -----------------------------
# URL PARAMETERS
# -----------------------------
params = st.query_params

# =====================================================
# OVERLAY MODE
# =====================================================
if params.get("mode") == "overlay":

    st.markdown("""
    <style>

    html, body, [data-testid="stAppViewContainer"], .main {
        background: transparent !important;
    }

    header, footer, #MainMenu {
        display: none !important;
    }

    .ticker-container {
        position: fixed;
        top: 15px;
        left: 15px;
        font-family: Arial, sans-serif;
    }

    .black-stripe {
        background: rgba(0,0,0,0.92);
        padding: 10px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-left: 5px solid #8BC34A;
        border-radius: 4px;
    }

    .runs {
        color: white;
        font-size: 42px;
        font-weight: 900;
    }

    .overs {
        color: white;
        font-size: 20px;
        opacity: 0.85;
    }

    </style>
    """, unsafe_allow_html=True)

    d = get_match()

    ov = f"{d['balls']//6}.{d['balls']%6}"

    st.markdown(
        f"""
        <div class="ticker-container">
            <div class="black-stripe">
                <div class="runs">{d['runs']}</div>
                <div class="overs">({ov}/{d['match_overs']})</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    time.sleep(2)
    st.rerun()

# =====================================================
# MAIN SCORING APP
# =====================================================
else:

    # -----------------------------
    # CSS
    # -----------------------------
    st.markdown("""
    <style>

    .stApp {
        background-color: #d3d3d3;
    }

    .block-container {
        max-width: 620px;
        padding-top: 10px;
        padding-left: 8px;
        padding-right: 8px;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    /* ---------------- HEADER ---------------- */

    .score-header {
        display: flex;
        justify-content: space-between;
        text-align: center;
        margin-bottom: 30px;
        padding: 0px 15px;
    }

    .score-box {
        flex: 1;
    }

    .lbl {
        display: block;
        font-size: 36px;
        font-weight: 500;
        color: black;
        font-family: Arial, sans-serif;
        margin-bottom: 6px;
    }

    .val {
        display: block;
        font-size: 92px;
        line-height: 1;
        font-weight: 900;
        color: black;
        font-family: Arial, sans-serif;
    }

    /* ---------------- GRID SPACING ---------------- */

    [data-testid="stHorizontalBlock"] {
        gap: 14px !important;
    }

    div[data-testid="column"] {
        padding: 0 !important;
    }

    /* ---------------- MAIN BUTTONS ---------------- */

    .stButton > button {

        width: 100% !important;
        height: 145px !important;

        background-color: black !important;
        color: white !important;

        border: none !important;
        border-radius: 0px !important;

        font-size: 52px !important;
        font-weight: 400 !important;

        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: #111 !important;
        color: white !important;
    }

    /* ---------------- SMALL BUTTONS ---------------- */

    .extra-btn .stButton > button {
        height: 72px !important;
        font-size: 20px !important;
        font-weight: 400 !important;
    }

    /* ---------------- UNDO BUTTON ---------------- */

    button[kind="secondary"] {
        font-size: 24px !important;
    }

    /* ---------------- SECTION HEADERS ---------------- */

    .section-hdr {

        background-color: black;
        color: white;

        text-align: center;

        font-size: 44px;
        font-weight: 400;

        padding-top: 10px;
        padding-bottom: 10px;

        margin-top: 18px;
        margin-bottom: 10px;

        font-family: Arial, sans-serif;
    }

    /* ---------------- RESET BUTTON ---------------- */

    .full-btn .stButton > button {

        height: 72px !important;

        font-size: 24px !important;
        font-weight: 400 !important;

        margin-top: 18px;

        background-color: black !important;
        color: white !important;

        border: none !important;
        border-radius: 0px !important;
    }

    </style>
    """, unsafe_allow_html=True)

    d = get_match()

    # -----------------------------
    # SESSION STATE
    # -----------------------------
    if "started" not in st.session_state:
        st.session_state.started = False

    # =====================================================
    # START SCREEN
    # =====================================================
    if not st.session_state.started:

        st.markdown(
            """
            <h1 style='
                text-align:center;
                color:black;
                margin-top:50px;
                font-family:Arial;
            '>
                Cricket Match Setup
            </h1>
            """,
            unsafe_allow_html=True
        )

        ov_in = st.number_input(
            "Match Overs",
            min_value=1,
            value=int(d["match_overs"])
        )

        st.markdown('<div class="full-btn">', unsafe_allow_html=True)

        if st.button("START MATCH"):

            supabase.table("match_data").update({
                "match_overs": ov_in,
                "runs": 0,
                "balls": 0,
                "target": 0,
                "history": "[]"
            }).eq("id", 1).execute()

            st.session_state.started = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # SCORING SCREEN
    # =====================================================
    else:

        # ---------------- HEADER ----------------

        st.markdown(
            f"""
            <div class="score-header">

                <div class="score-box">
                    <span class="lbl">SCORE</span>
                    <span class="val">{d['runs']}</span>
                </div>

                <div class="score-box">
                    <span class="lbl">OVERS</span>
                    <span class="val">
                        {d['balls']//6}.{d['balls']%6}
                    </span>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # =====================================================
        # ROW 1
        # =====================================================

        row1 = st.columns(3)

        with row1[0]:
            if st.button("1", key="1"):
                update_score(1, 1)
                st.rerun()

        with row1[1]:
            if st.button("2", key="2"):
                update_score(2, 1)
                st.rerun()

        with row1[2]:
            if st.button("3", key="3"):
                update_score(3, 1)
                st.rerun()

        # =====================================================
        # ROW 2
        # =====================================================

        row2 = st.columns(3)

        with row2[0]:
            if st.button("4", key="4"):
                update_score(4, 1)
                st.rerun()

        with row2[1]:
            if st.button("6", key="6"):
                update_score(6, 1)
                st.rerun()

        with row2[2]:
            if st.button("UNDO", key="undo"):
                update_score(0, 0, is_undo=True)
                st.rerun()

        # =====================================================
        # WIDES
        # =====================================================

        st.markdown(
            '<div class="section-hdr">Wides</div>',
            unsafe_allow_html=True
        )

        wcols = st.columns(5)

        for i in range(5):

            with wcols[i]:

                st.markdown('<div class="extra-btn">', unsafe_allow_html=True)

                if st.button(f"W+{i}", key=f"w{i}"):

                    update_score(1 + i, 0)
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # NO BALL
        # =====================================================

        st.markdown(
            '<div class="section-hdr">No Ball</div>',
            unsafe_allow_html=True
        )

        ncols = st.columns(7)

        for i in range(7):

            with ncols[i]:

                st.markdown('<div class="extra-btn">', unsafe_allow_html=True)

                if st.button(f"N+{i}", key=f"n{i}"):

                    update_score(1 + i, 0)
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # RESET BUTTON
        # =====================================================

        st.markdown('<div class="full-btn">', unsafe_allow_html=True)

        if st.button("Reset Match", key="reset"):

            st.session_state.started = False

            supabase.table("match_data").update({
                "runs": 0,
                "balls": 0,
                "target": 0,
                "history": "[]"
            }).eq("id", 1).execute()

            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
