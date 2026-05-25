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

# 1. OVERLAY VIEW (Transparent Ticker for Prism/CameraFi)
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            /* Hide all Streamlit elements and make background transparent */
            [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
                background-color: rgba(0,0,0,0) !important;
            }
            header, footer, #MainMenu {visibility: hidden;}
            .block-container {padding: 0 !important; margin: 0 !important;}
            
            /* Ticker Styling - Top Left */
            .ticker-box {
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 12px 18px;
                border-radius: 8px;
                border-left: 6px solid #8bc34a;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                min-width: 180px;
                backdrop-filter: blur(4px);
                box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            }
        </style>
    """, unsafe_allow_html=True)
    
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    
    st.markdown(f"""
        <div class="ticker-box">
            <div style="font-size: 10px; font-weight: bold; color: #8bc34a; letter-spacing: 1.5px; margin-bottom: 2px;">LIVE MATCH</div>
            <div style="font-size: 28px; font-weight: 900; line-height: 1;">
                {d['runs']} <span style="font-size: 16px; font-weight: 400; opacity: 0.9;">({ov})</span>
            </div>
            {f'<div style="font-size: 12px; margin-top: 5px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 3px; font-weight:bold;">TGT: {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)
    st.rerun()

# 2. MAIN APP (Scorer Interface)
else:
    # Styling for the Scorer Buttons
    st.markdown("""
        <style>
        .stButton>button { height: 85px; font-size: 24px !important; font-weight: bold; border-radius: 12px; }
        /* Boundary Buttons Highlight */
        div[data-testid="column"]:nth-of-type(2) .stButton>button, 
        div[data-testid="column"]:nth-of-type(3) .stButton>button { border-bottom: 5px solid #8bc34a; }
        [data-testid="stMetricValue"] { font-size: 45px !important; color: #2e7d32; }
        </style>
    """, unsafe_allow_html=True)

    if "started" not in st.session_state:
        st.session_state.started = False

    d = get_match()

    # START SCREEN
    if not st.session_state.started:
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

        # Scoring Grid 0, 1, 2
        c1, c2, c3 = st.columns(3)
