import streamlit as st
from supabase import create_client

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- APP CONFIG ---
st.set_page_config(page_title="Cricket Pro Scorer", layout="centered")

# CSS for a professional grid and UI
st.markdown("""
    <style>
    .stButton>button { height: 80px; font-size: 24px !important; font-weight: bold; border-radius: 10px; }
    .out-btn button { background-color: #ff4b4b !important; color: white !important; }
    .boundary-btn button { border: 2px solid #8bc34a !important; }
    [data-testid="stMetricValue"] { font-size: 48px !important; }
    </style>
""", unsafe_allow_html=True)

# --- DATA HELPERS ---
def get_match():
    return supabase.table("match_data").select("*").eq("id", 1).single().execute().data

def update_db(updates):
    supabase.table("match_data").update(updates).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. OVERLAY VIEW
if params.get("mode") == "overlay":
    st.empty()
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.8); color: white; padding: 15px; border-radius: 15px; border-left: 10px solid #8bc34a; width: fit-content; font-family: sans-serif;">
            <div style="font-size: 14px; opacity: 0.8;">LIVE MATCH</div>
            <div style="font-size: 36px; font-weight: bold;">{d['runs']} <span style="font-size: 20px; font-weight: normal;">({ov}/{d['match_overs']})</span></div>
            {f'<div style="font-size: 16px; color: #8bc34a;">TARGET: {d["target"]}</div>' if d['target'] > 0 else ''}
        </div>
    """, unsafe_allow_html=True)
    st.rerun()

# 2. MAIN APP
else:
    # Initialize session state for the start screen
    if "started" not in st.session_state:
        st.session_state.started = False

    d = get_match()

    # START SCREEN
    if not st.session_state.started:
        st.title("🏏 Match Setup")
        overs = st.number_input("Select Match Overs", min_value=1, max_value=50, value=int(d['match_overs']))
        target = st.number_input("Set Target (0 if 1st Innings)", min_value=0, value=int(d['target']))
        
        if st.button("START MATCH", use_container_width=True, type="primary"):
            update_db({"match_overs": overs, "target": target, "runs": 0, "balls": 0})
            st.session_state.started = True
            st.rerun()

    # SCORING SCREEN
    else:
        # Header Metrics
        col_m1, col_m2 = st.columns(2)
        ov_display = f"{d['balls']//6}.{d['balls']%6}"
        col_m1.metric("RUNS", d['runs'])
        col_m2.metric("OVERS", f"{ov_display} / {d['match_overs']}")

        st.divider()

        # SCORING GRID (3x4 Layout)
        # Row 1: 0, 1, 2
        r1c1, r1c2, r1c3 = st.columns(3)
        if r1c1.button("0", use_container_width=True): 
            update_db({"runs": d['runs'], "balls": d['balls']+1}); st.rerun()
        if r1c2.button("1", use_container_width=True): 
            update_db({"runs": d['runs']+1, "balls": d['balls']+1}); st.rerun()
        if r1c3.button("2", use_container_width=True): 
            update_db({"runs": d['runs']+2, "balls": d['balls']+1}); st.rerun()

        # Row 2: 3, 4, 6
        r2c1, r2c2, r2c3 = st.columns(3)
        if r2c1.button("3", use_container_width=True): 
            update_db({"runs": d['runs']+3, "balls": d['balls']+1}); st.rerun()
        with r2c2: st.markdown('<div class="boundary-btn">', unsafe_allow_html=True)
        if r2c2.button("4", use_container_width=True): 
            update_db({"runs": d['runs']+4, "balls": d['balls']+1}); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        with r2c3: st.markdown('<div class="boundary-btn">', unsafe_allow_html=True)
        if r2c3.button("6", use_container_width=True): 
            update_db({"runs": d['runs']+6, "balls": d['balls']+1}); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Row 3: WD, NB, Reset
        r3c1, r3c2, r3c3 = st.columns(3)
        
        # WIDE LOGIC (No Ball increase)
        with r3c1:
            with st.popover("WD", use_container_width=True):
                st.write("Extra runs on Wide?")
                extra_wd = st.radio("Runs", [0, 1, 2, 3, 4, 6], horizontal=True, key="wd_sel")
                if st.button("Confirm Wide"):
                    update_db({"runs": d['runs'] + 1 + extra_wd})
                    st.rerun()

        # NO BALL LOGIC (No Ball increase)
        with r3c2:
            with st.popover("NB", use_container_width=True):
                st.write("Extra runs on No Ball?")
                extra_nb = st.radio("Runs", [0, 1, 2, 3, 4, 6], horizontal=True, key="nb_sel")
                if st.button("Confirm No Ball"):
                    update_db({"runs": d['runs'] + 1 + extra_nb})
                    st.rerun()

        if r3c3.button("🔄", use_container_width=True):
            st.session_state.started = False
            st.rerun()

        # --- OVERLAY TOOLS ---
        st.divider()
        overlay_url = f"https://{st.get_option('browser.gatherUsageStats') or 'your-app'}.streamlit.app/?mode=overlay"
        if st.button("📋 Copy Overlay Link", use_container_width=True):
            st.code(overlay_url)
            st.success("Copy the link above into Prism/CameraFi")
