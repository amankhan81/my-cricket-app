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

# 1. OVERLAY VIEW (Transparent + Black Stripe)
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .block-container {padding: 0 !important; margin: 0 !important;}
            .ticker-container { position: fixed; top: 15px; left: 15px; font-family: sans-serif; }
            .green-header { background: #1B5E20; color: white; padding: 5px 15px; border-radius: 8px 8px 0 0; font-size: 10px; font-weight: bold; }
            .black-stripe { background: rgba(0, 0, 0, 0.9); padding: 10px 15px; display: flex; align-items: baseline; gap: 10px; color: white !important; border-left: 4px solid #8bc34a; }
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
            <div class="black-stripe"><span class="runs-txt">{d['runs']}</span><span class="ov-txt">({ov}/{d['match_overs']})</span></div>
            {f'<div class="target-box">TGT: {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)
    import time
    time.sleep(2)
    st.rerun()

# 2. MOBILE SCORER APP (Dark Grey Edition)
else:
    st.markdown("""
        <style>
            /* Base Background */
            .stApp { background-color: #CCCCCC !important; }
            .block-container { padding: 10px !important; }

            /* Header Typography */
            .score-header { display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; padding-top: 10px; }
            .lbl { color: black; font-size: 32px; font-weight: bold; font-family: sans-serif; letter-spacing: 1px; }
            .val { color: black; font-size: 85px; font-weight: 900; display: block; margin-top: -15px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }

            /* Grid Layout Setup */
            div[data-testid="stHorizontalBlock"] {
                display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 15px !important;
            }
            div[data-testid="stColumn"] { flex: 1 !important; min-width: 0 !important; }

            /* Square Black Buttons */
            .stButton > button {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                background-color: black !important;
                color: white !important;
                font-size: 40px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            /* Section Headers */
            .section-hdr { background-color: black; color: white; text-align: center; font-size: 35px; font-weight: bold; padding: 10px; margin: 15px 0 5px 0; }
            
            /* Horizontal Extras Row */
            .extra-btn button {
                aspect-ratio: auto !important;
                height: 60px !important;
                font-size: 22px !important;
                border: 1px solid #444 !important;
            }

            /* Start Match Button Styling */
            .start-btn button {
                aspect-ratio: auto !important;
                height: 70px !important;
                background-color: black !important;
                color: white !important;
                font-size: 24px !important;
                border-radius: 4px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    if "started" not in st.session_state: st.session_state.started = False

    # --- START SCREEN ---
    if not st.session_state.started:
        st.markdown("<h1 style='color:black; text-align:center;'>Cricket Match Setup</h1>", unsafe_allow_html=True)
        ov_in = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        
        st.markdown('<div class="start-btn">', unsafe_allow_html=True)
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_in, "runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SCORING INTERFACE ---
    else:
        # Score & Overs Display
        st.markdown(f"""
            <div class="score-header">
                <div><span class="lbl">SCORE</span><span class="val">{d['runs']}</span></div>
                <div><span class="lbl">OVERS</span><span class="val">{d['balls']//6}.{d['balls']%6}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # Main Grid (1, 2, 3 / 4, 6, UNDO)
        r1c1, r1c2, r1c3 = st.columns(3)
        if r1c1.button("1", key="1"): update_db(1, 1); st.rerun()
        if r1c2.button("2", key="2"): update_db(2, 1); st.rerun()
        if r1c3.button("3", key="3"): update_db(3, 1); st.rerun()

        r2c1, r2c2, r2c3 = st.columns(3)
        if r2c1.button("4", key="4"): update_db(4, 1); st.rerun()
        if r2c2.button("6", key="6"): update_db(6, 1); st.rerun()
        if r2c3.button("UNDO", key="un"): update_db(-1, -1); st.rerun()

        # Wides
        st.markdown('<div class="section-hdr">Wides</div>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for i in range(5):
            with wcols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if wcols[i].button(f"W+{i}", key=f"w{i}"): update_db(1+i, 0); st.rerun()

        # No Ball
        st.markdown('<div class="section-hdr">No Ball</div>', unsafe_allow_html=True)
        ncols = st.columns(7)
        for i in range(7):
            with ncols[i]: st.markdown('<div class="extra-btn">', unsafe_allow_html=True)
            if ncols[i].button(f"N+{i}", key=f"n{i}"): update_db(1+i, 0); st.rerun()

        # Reset Match Button
        st.markdown('<br><div class="start-btn">', unsafe_allow_html=True)
        if st.button("Reset Match", key="reset"):
            st.session_state.started = False
            supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
