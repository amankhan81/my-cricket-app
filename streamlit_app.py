import streamlit as st
from supabase import create_client

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- APP CONFIG ---
st.set_page_config(page_title="Cricket Pro Scorer", layout="centered")

# --- DATA HELPERS ---
def get_match():
    return supabase.table("match_data").select("*").eq("id", 1).single().execute().data

def update_db(updates):
    supabase.table("match_data").update(updates).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. OVERLAY VIEW (Ticker with forced transparency)
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            /* FORCE TOTAL TRANSPARENCY */
            html, body, [data-testid="stAppViewContainer"], 
            [data-testid="stHeader"], .main, .block-container {
                background-color: rgba(0,0,0,0) !important;
                background: transparent !important;
            }
            header, footer, #MainMenu {visibility: hidden; display: none;}
            
            /* Remove Streamlit padding/animations */
            .block-container {padding: 0 !important; margin: 0 !important;}
            .stApp { overflow: hidden; }
            
            /* Disable Fading/Transition Animations */
            * { transition: none !important; animation: none !important; }

            .ticker-container {
                position: absolute;
                top: 20px;
                left: 20px;
                font-family: 'Arial Black', Gadget, sans-serif;
                display: flex;
                flex-direction: column;
                gap: 0px;
            }

            .main-box {
                background: #8bc34a; /* Green */
                padding: 10px 18px;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                min-width: 200px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
            }

            .innings-label {
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 2px;
            }

            .score-row {
                display: flex;
                align-items: baseline;
                gap: 8px;
                color: white; /* Forced white text */
            }

            .runs {
                font-size: 34px;
                font-weight: 900;
                line-height: 1;
            }

            .overs {
                font-size: 18px;
                font-weight: 600;
            }

            .target-box {
                background: #1a1a1a;
                color: white;
                padding: 4px 12px;
                border-radius: 0 0 6px 6px;
                font-size: 13px;
                font-weight: bold;
                width: fit-content;
                margin-left: 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    label = "1ST INNINGS" if d['target'] == 0 else "2ND INNINGS"
    
    st.markdown(f"""
        <div class="ticker-container">
            <div class="main-box">
                <div class="innings-label">{label}</div>
                <div class="score-row">
                    <span class="runs">Score {d['runs']}</span>
                    <span class="overs">Overs {ov} ({d['match_overs']})</span>
                </div>
            </div>
            {f'<div class="target-box">Target {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)
    st.rerun()

# 2. MAIN APP (Scorer Phone Interface)
else:
    st.markdown("""
        <style>
        .stButton>button { height: 80px; font-size: 22px !important; font-weight: bold; border-radius: 10px; }
        div[data-testid="column"]:nth-of-type(2) .stButton>button, 
        div[data-testid="column"]:nth-of-type(3) .stButton>button { border-bottom: 5px solid #8bc34a; }
        </style>
    """, unsafe_allow_html=True)

    if "started" not in st.session_state:
        st.session_state.started = False

    d = get_match()
    max_balls = d['match_overs'] * 6

    # INNINGS COMPLETE PROMPT
    if d['balls'] >= max_balls:
        st.warning(f"Innings Complete! {d['match_overs']} Overs finished.")
        if st.button("START NEXT INNINGS", use_container_width=True, type="primary"):
            # Set target as current runs + 1 and reset score/balls
            update_db({"target": d['runs'] + 1, "runs": 0, "balls": 0})
            st.rerun()
        if st.button("New Match / Reset Entirely", use_container_width=True):
            st.session_state.started = False
            update_db({"target": 0, "runs": 0, "balls": 0})
            st.rerun()

    # START SCREEN
    elif not st.session_state.started:
        st.title("🏏 Match Setup")
        overs = st.number_input("Match Overs", min_value=1, value=int(d['match_overs']))
        target = st.number_input("Target (0 if 1st Innings)", min_value=0, value=int(d['target']))
        
        if st.button("START MATCH", use_container_width=True, type="primary"):
            update_db({"match_overs": overs, "target": target, "runs": 0, "balls": 0})
            st.session_state.started = True
            st.rerun()

    # SCORING SCREEN
    else:
        m1, m2 = st.columns(2)
        ov_disp = f"{d['balls']//6}.{d['balls']%6}"
        m1.metric("RUNS", d['runs'])
        m2.metric("OVERS", f"{ov_disp} / {d['match_overs']}")

        c1, c2, c3 = st.columns(3)
        if c1.button("0", use_container_width=True): update_db({"runs": d['runs'], "balls": d['balls']+1}); st.rerun()
        if c2.button("1", use_container_width=True): update_db({"runs": d['runs']+1, "balls": d['balls']+1}); st.rerun()
        if c3.button("2", use_container_width=True): update_db({"runs": d['runs']+2, "balls": d['balls']+1}); st.rerun()

        c4, c5, c6 = st.columns(3)
        if c4.button("3", use_container_width=True): update_db({"runs": d['runs']+3, "balls": d['balls']+1}); st.rerun()
        if c5.button("4\nBNDRY", use_container_width=True): update_db({"runs": d['runs']+4, "balls": d['balls']+1}); st.rerun()
        if c6.button("6\nBNDRY", use_container_width=True): update_db({"runs": d['runs']+6, "balls": d['balls']+1}); st.rerun()

        c7, c8, c9 = st.columns(3)
        with c7:
            with st.popover("WD", use_container_width=True):
                ex_wd = st.selectbox("Plus Runs", [0,1,2,3,4,6], key="wd")
                if st.button("OK", key="ok_wd", use_container_width=True):
                    update_db({"runs": d['runs'] + 1 + ex_wd})
                    st.rerun()
        with c8:
            with st.popover("NB", use_container_width=True):
                ex_nb = st.selectbox("Plus Runs", [0,1,2,3,4,6], key="nb")
                if st.button("OK", key="ok_nb", use_container_width=True):
                    update_db({"runs": d['runs'] + 1 + ex_nb})
                    st.rerun()
        
        if c9.button("⚙️", use_container_width=True):
            st.session_state.started = False
            st.rerun()
