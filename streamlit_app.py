import streamlit as st
from supabase import create_client

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    # We use a volatile query to ensure we aren't getting cached data
    return supabase.table("match_data").select("*").eq("id", 1).single().execute().data

def update_db(runs_inc, balls_inc):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + runs_inc,
        "balls": d['balls'] + balls_inc
    }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. OVERLAY VIEW (Fixed Update Issue + Black Stripe)
if params.get("mode") == "overlay":
    # Aggressive CSS to force transparency and layout
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { 
                background: transparent !important; 
            }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}

            .ticker-container {
                position: fixed; top: 15px; left: 15px;
                font-family: 'Arial Black', sans-serif;
            }

            .main-box {
                background: #1B5E20; /* Dark Green */
                padding: 10px 20px;
                border-radius: 8px 8px 0 0;
                min-width: 240px;
                border-bottom: 3px solid #8bc34a;
            }

            /* BLACK STRIPE FOR VISIBILITY */
            .black-stripe {
                background: rgba(0, 0, 0, 0.85);
                padding: 5px 15px;
                display: flex;
                align-items: baseline;
                gap: 12px;
                color: white !important;
            }

            .runs-text { font-size: 36px; font-weight: 900; color: white !important; line-height: 1; }
            .overs-text { font-size: 18px; font-weight: bold; color: white !important; opacity: 0.9; }

            .target-box {
                background: #ffeb3b; /* Yellow warning style for target */
                color: black;
                padding: 4px 12px;
                border-radius: 0 0 8px 8px;
                font-size: 14px;
                font-weight: 900;
                width: fit-content;
                margin-left: 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Logic to fetch data every run
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    label = "1ST INNINGS" if d['target'] == 0 else "2ND INNINGS"

    st.markdown(f"""
        <div class="ticker-container">
            <div class="main-box">
                <div style="color:white; font-size:10px; letter-spacing:2px; font-weight:bold; margin-bottom:5px;">{label}</div>
                <div class="black-stripe">
                    <span class="runs-text">{d['runs']}</span>
                    <span class="overs-text">({ov})</span>
                </div>
            </div>
            {f'<div class="target-box">TARGET: {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)

    # Force the app to refresh every 2 seconds to check Supabase
    import time
    time.sleep(2)
    st.rerun()

# 2. MOBILE SCORER APP
else:
    st.markdown("""
        <style>
            .stApp { background-color: #FEE49B !important; }
            [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; gap: 8px !important; }
            .stButton>button {
                height: 90px !important; font-size: 32px !important; font-weight: 800 !important;
                border-radius: 8px !important; border: none !important; color: white !important;
            }
            /* Row 1: 1, 2, 3 (Dark Blue/Grey) */
            div[data-testid="column"]:nth-of-type(1) button { background-color: #4A90E2 !important; }
            div[data-testid="column"]:nth-of-type(2) button { background-color: #2c3e50 !important; }
            div[data-testid="column"]:nth-of-type(3) button { background-color: #1a1a1a !important; }
            /* Row 2: 4, 6 (Green/Bright Blue) and Undo (Peach) */
            .four-btn button { background-color: #00B050 !important; }
            .six-btn button { background-color: #0070C0 !important; }
            .undo-btn button { background-color: #F8B195 !important; color: black !important; font-size: 18px !important; }
            .extra-hdr { background: #C65911; color: white; text-align: center; font-weight: bold; padding: 5px; margin: 10px 0; border-radius: 4px; }
            summary { color: black !important; font-weight: bold !important; }
        </style>
    """, unsafe_allow_html=True)

    if "started" not in st.session_state:
        st.session_state.started = False

    d = get_match()
    max_balls = d['match_overs'] * 6

    if not st.session_state.started:
        st.title("🏏 Match Setup")
        ov_input = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_input, "runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()

    elif d['balls'] >= max_balls and d['target'] == 0:
        st.header("Innings Over!")
        if st.button("START 2nd INNINGS", use_container_width=True):
            update_db(0, 0) # Trigger fetch
            supabase.table("match_data").update({"target": d['runs'] + 1, "runs": 0, "balls": 0}).eq("id", 1).execute()
            st.rerun()

    else:
        # Scoreboard
        m1, m2 = st.columns(2)
        m1.metric("SCORE", d['runs'])
        m2.metric("OVERS", f"{d['balls']//6}.{d['balls']%6}")

        # Grid
        c1, c2, c3 = st.columns(3)
        if c1.button("1", key="b1", use_container_width=True): update_db(1, 1); st.rerun()
        if c2.button("2", key="b2", use_container_width=True): update_db(2, 1); st.rerun()
        if c3.button("3", key="b3", use_container_width=True): update_db(3, 1); st.rerun()

        c4, c5, c6 = st.columns(3)
        with c4: st.markdown('<div class="four-btn">', unsafe_allow_html=True)
        if c4.button("4", key="b4", use_container_width=True): update_db(4, 1); st.rerun()
        with c5: st.markdown('<div class="six-btn">', unsafe_allow_html=True)
        if c5.button("6", key="b6", use_container_width=True): update_db(6, 1); st.rerun()
        with c6: st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
        if c6.button("UNDO", key="und", use_container_width=True): update_db(-1, -1); st.rerun()

        # Extras
        st.markdown('<div class="extra-hdr">WIDES</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            if wcols[i].button(f"W+{i}", key=f"w{i}", use_container_width=True): update_db(1+i, 0); st.rerun()

        st.markdown('<div class="extra-hdr">NO BALL</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            if ncols[i].button(f"N+{i}", key=f"n{i}", use_container_width=True): update_db(1+i, 0); st.rerun()

        with st.expander("⚙️ Settings"):
            if st.button("RESET MATCH"):
                st.session_state.started = False
                supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
                st.rerun()
