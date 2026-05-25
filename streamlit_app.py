import streamlit as st
from supabase import create_client

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    return supabase.table("match_data").select("*").eq("id", 1).single().execute().data

def update_db(runs_inc, balls_inc):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + runs_inc,
        "balls": d['balls'] + balls_inc
    }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. OVERLAY VIEW (Transparent + Black Stripe + Match Overs)
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}

            .ticker-container { position: fixed; top: 15px; left: 15px; font-family: sans-serif; }
            .green-header { background: #1B5E20; color: white; padding: 5px 15px; border-radius: 8px 8px 0 0; font-size: 10px; font-weight: bold; letter-spacing: 1px; }
            
            /* THE BLACK STRIPE */
            .black-stripe { 
                background: rgba(0, 0, 0, 0.9); 
                padding: 10px 15px; 
                display: flex; 
                align-items: baseline; 
                gap: 10px; 
                color: white !important;
                border-left: 4px solid #8bc34a;
            }
            .runs-txt { font-size: 38px; font-weight: 900; line-height: 1; color: white !important; }
            .ov-txt { font-size: 18px; font-weight: bold; color: white !important; opacity: 0.8; }

            .target-box { background: #ffeb3b; color: black; padding: 3px 12px; border-radius: 0 0 8px 8px; font-size: 13px; font-weight: 900; width: fit-content; margin-left: 10px; }
        </style>
    """, unsafe_allow_html=True)
    
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    label = "1ST INNINGS" if d['target'] == 0 else "2ND INNINGS"

    st.markdown(f"""
        <div class="ticker-container">
            <div class="green-header">{label}</div>
            <div class="black-stripe">
                <span class="runs-txt">{d['runs']}</span>
                <span class="ov-txt">({ov}/{d['match_overs']})</span>
            </div>
            {f'<div class="target-box">TGT: {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)

    import time
    time.sleep(2)
    st.rerun()

# 2. MOBILE SCORER APP (Forced Grid)
else:
    st.markdown("""
        <style>
            .stApp { background-color: #FEE49B !important; }
            
            /* Score Header Styling */
            .score-header { display: flex; justify-content: space-around; padding: 10px; text-align: center; }
            .lbl { color: #4A90E2; font-size: 24px; font-weight: bold; }
            .val { color: black; font-size: 60px; font-weight: 900; display: block; margin-top: -10px; }

            /* BUTTON GRID (FORCING 3 COLUMNS) */
            .stButton > button {
                height: 85px !important; font-size: 30px !important; font-weight: 800 !important;
                border-radius: 8px !important; color: white !important; border: none !important;
            }
            
            /* Aligning buttons in rows even on mobile */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 10px !important;
            }
            div[data-testid="stColumn"] { flex: 1 !important; min-width: 0 !important; }

            /* Colors */
            .btn-blue button { background-color: #4A90E2 !important; }
            .btn-dark button { background-color: #2c3e50 !important; }
            .btn-green button { background-color: #00B050 !important; }
            .btn-deepblue button { background-color: #0070C0 !important; }
            .btn-undo button { background-color: #F8B195 !important; color: black !important; font-size: 18px !important; }
            
            .extra-title { background: #C65911; color: white; text-align: center; font-weight: bold; padding: 6px; margin: 10px 0; border-radius: 4px; }
            .stExpander summary { color: black !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    max_balls = d['match_overs'] * 6

    if "started" not in st.session_state: st.session_state.started = False

    # START SCREEN
    if not st.session_state.started:
        st.title("🏏 Match Setup")
        ov_in = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_in, "runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()

    # NEXT INNINGS PROMPT
    elif d['balls'] >= max_balls and d['target'] == 0:
        st.header("Innings Complete!")
        if st.button("START 2nd INNINGS", use_container_width=True):
            supabase.table("match_data").update({"target": d['runs'] + 1, "runs": 0, "balls": 0}).eq("id", 1).execute()
            st.rerun()

    # SCORING BOARD
    else:
        # Score display
        st.markdown(f"""
            <div class="score-header">
                <div><span class="lbl">SCORE</span><span class="val">{d['runs']}</span></div>
                <div><span class="lbl">OVERS</span><span class="val">{d['balls']//6}.{d['balls']%6}</span></div>
            </div>
        """, unsafe_allow_html=True)

        if d['target'] > 0: st.info(f"Target: {d['target']} | Need {d['target']-d['runs']} from {max_balls-d['balls']} balls")

        # Row 1: 1, 2, 3
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        if c1.button("1", key="1"): update_db(1, 1); st.rerun()
        with c2: st.markdown('<div class="btn-dark">', unsafe_allow_html=True)
        if c2.button("2", key="2"): update_db(2, 1); st.rerun()
        with c3: st.markdown('<div class="btn-dark">', unsafe_allow_html=True)
        if c3.button("3", key="3"): update_db(3, 1); st.rerun()

        # Row 2: 4, 6, UNDO
        c4, c5, c6 = st.columns(3)
        with c4: st.markdown('<div class="btn-green">', unsafe_allow_html=True)
        if c4.button("4", key="4"): update_db(4, 1); st.rerun()
        with c5: st.markdown('<div class="btn-deepblue">', unsafe_allow_html=True)
        if c5.button("6", key="6"): update_db(6, 1); st.rerun()
        with c6: st.markdown('<div class="btn-undo">', unsafe_allow_html=True)
        if c6.button("UNDO", key="un"): update_db(-1, -1); st.rerun()

        # Wides
        st.markdown('<div class="extra-title">WIDES</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            with wcols[i]: st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
            if wcols[i].button(f"W{i}", key=f"w{i}"): update_db(1+i, 0); st.rerun()

        # No Balls
        st.markdown('<div class="extra-title">NO BALL</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            with ncols[i]: st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
            if ncols[i].button(f"N{i}", key=f"n{i}"): update_db(1+i, 0); st.rerun()

        with st.expander("⚙️ Settings"):
            if st.button("RESET ALL"):
                st.session_state.started = False
                supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
                st.rerun()
