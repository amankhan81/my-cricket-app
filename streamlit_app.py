import streamlit as st
from supabase import create_client
import json
import time

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Cricket Scorer",
    layout="centered"
)

# =====================================================
# SUPABASE
# =====================================================

URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"

supabase = create_client(URL, KEY)

# =====================================================
# DATABASE FUNCTIONS
# =====================================================

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


# =====================================================
# URL PARAMS
# =====================================================

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
# MAIN APP
# =====================================================

else:

    # =====================================================
    # CSS
    # =====================================================

    st.markdown("""
    <style>

    /* =====================================================
       APP
    ===================================================== */

    .stApp {
        background-color: #d3d3d3;
    }

    .block-container {

        max-width: 430px !important;

        padding-top: 8px !important;
        padding-left: 6px !important;
        padding-right: 6px !important;
        padding-bottom: 20px !important;
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }

    /* =====================================================
       HEADER
    ===================================================== */

    .score-header {

        display: flex;
        justify-content: space-between;

        text-align: center;

        margin-bottom: 22px;

        padding-left: 10px;
        padding-right: 10px;
    }

    .score-box {
        width: 48%;
    }

    .lbl {

        display: block;

        color: black;

        font-size: 34px;
        font-weight: 500;

        font-family: Arial, sans-serif;

        margin-bottom: 2px;
    }

    .val {

        display: block;

        color: black;

        font-size: 88px;
        line-height: 1;

        font-weight: 900;

        font-family: Arial, sans-serif;

        text-shadow: 2px 2px 2px rgba(0,0,0,0.3);
    }

    /* =====================================================
       ROW SPACING
    ===================================================== */

    [data-testid="stHorizontalBlock"] {
        gap: 10px !important;
    }

    div[data-testid="column"] {
        padding: 0 !important;
    }

    /* =====================================================
       MAIN BUTTONS
    ===================================================== */

    .stButton > button {

        width: 100% !important;

        height: 145px !important;

        background-color: black !important;
        color: white !important;

        border: none !important;
        border-radius: 0px !important;

        font-size: 52px !important;
        font-weight: 400 !important;

        font-family: Arial, sans-serif;

        box-shadow: none !important;
    }

    .stButton > button:hover {

        background-color: #111 !important;
        color: white !important;
    }

    /* =====================================================
       UNDO BUTTON
    ===================================================== */

    div[data-testid="column"]:nth-child(3) .stButton > button {

        font-size: 22px !important;
    }

    /* =====================================================
       SECTION TITLES
    ===================================================== */

    .section-hdr {

        width: 100%;

        background-color: black;
        color: white;

        text-align: center;

        font-size: 42px;
        font-weight: 400;

        font-family: Arial, sans-serif;

        padding-top: 10px;
        padding-bottom: 10px;

        margin-top: 12px;
        margin-bottom: 8px;
    }

    /* =====================================================
       SMALL BUTTONS
    ===================================================== */

    .extra-btn .stButton > button {

        height: 72px !important;

        font-size: 18px !important;
        font-weight: 400 !important;

        padding: 0 !important;
    }

    /* =====================================================
       RESET BUTTON
    ===================================================== */

    .full-btn .stButton > button {

        width: 78% !important;

        margin-left: auto !important;
        margin-right: auto !important;

        display: block !important;

        height: 72px !important;

        background-color: black !important;
        color: white !important;

        border: none !important;
        border-radius: 0px !important;

        font-size: 24px !important;
        font-weight: 400 !important;

        margin-top: 16px !important;
    }

    </style>
    """, unsafe_allow_html=True)

    d = get_match()

    # =====================================================
    # SESSION
    # =====================================================

    if "started" not in st.session_state:
        st.session_state.started = True

    # =====================================================
    # SCORE HEADER
    # =====================================================

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

        supabase.table("match_data").update({
            "runs": 0,
            "balls": 0,
            "target": 0,
            "history": "[]"
        }).eq("id", 1).execute()

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
