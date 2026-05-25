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

# 1. OVERLAY VIEW
if params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"], .main { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .ticker-container { position: fixed; top: 15px; left: 15px; font-family: sans-serif; }
            .black-stripe { background: rgba(0, 0, 0, 0.9); padding: 10px 15px; display: flex; align-items: baseline; gap: 10px; color: white !important; border-left: 4px solid #8bc34a; border-radius: 4px; }
            .runs-txt { font-size: 38px; font-weight: 900; line-height: 1; color: white !important; }
            .ov-txt { font-size: 18px; font-weight: bold; color: white !important; opacity: 0.8; }
        </style>
    """, unsafe_allow_html=True)
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    st.markdown(f"""
        <div class="ticker-container">
            <div class="black-stripe"><span class="runs-txt">{d['runs']}</span><span class="ov-txt">({ov}/{d['match_overs']})</span></div>
        </div>
    """, unsafe_allow_html=True)
    import time
    time.sleep(2)
    st.rerun()

# 2. MOBILE SCORER APP
else:
    st.markdown("""
        <style>
            .stApp { background-color: #CCCCCC !important; }
            .block-container { padding: 10px !important; }

            /* Adjusted Header Font Sizes */
            .score-header { display: flex; justify-content: space-around; text-align: center; margin-bottom: 10px; }
            .lbl { color: black; font-size: 22px; font-weight: bold; }
            .val { color: black; font-size: 55px; font-weight: 900; display: block; margin-top: -5px; }

            /* FORCED GRID FOR 2:2 BUTTONS */
            [data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 5px !important;
                align-items: stretch !important;
            }
            [data-testid="stColumn"] {
                flex: 1 1 0% !important;
                min-width: 0 !important;
            }

            /* Main Buttons Styling */
            .stButton > button {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                background-color: black !important;
                color: white !important;
                font-size: 28px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 0px !important;
                padding: 0px !important;
            }
            
            /* Smaller Font for Extras */
            .extra-btn button {
                aspect-ratio: auto !important;
                height: 50px !important;
                font-size: 16px !important;
            }

            .section-hdr { background-color: black; color: white; text-align: center; font-size: 24px; font-weight: bold; padding: 8px; margin: 15px 0 5px 0; }
            
            /* Full width reset button */
            .reset-btn button {
                aspect-ratio: auto !important;
                height: 60px !important;
                font-size: 20px !important;
                border-radius: 4px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    d = get_match()
    if "started" not in st.session_state: st.session_state.started = False

    # --- START SCREEN ---
    if not st.session_state.started:
        st.markdown("<h2 style='color:black; text-align:center;'>Match Setup</h2>", unsafe_allow_html=True)
        ov_in = st.number_input("Overs", min_value=1, value=int(d['match_overs']))
        st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
        if st.button("START MATCH", use_container_width=True):
            supabase.table("match_data").update({"match_overs": ov_in, "runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.session_state.started = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SCORING INTERFACE ---
    else:
        st.markdown(f"""
            <div class="score-header">
                <div><span class="lbl">SCORE</span><span class="val">{d['runs']}</span></div>
                <div><span class="lbl">OVERS</span><span class="val">{d['balls']//6}.{d['balls']%6}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # Row 1: 1, 2, 3 (Forced Equal Size)
        r1 = st.columns(3)
        if r1[0].button("1", key="1"): update_db(1, 1); st.rerun()
        if r1[1].button("2", key="2"): update_db(2, 1); st.rerun()
        if r1[2].button("3", key="3"): update_db(3, 1); st.rerun()

        # Row 2: 4, 6, UNDO (Forced Equal Size)
        r2 = st.columns(3)
        if r2[0].button("4", key="4"): update_db(4, 1); st.rerun()
        if r2[1].button("6", key="6"): update_db(6, 1); st.rerun()
        if r2[2].button("UNDO", key="un"): update_db(-1, -1); st.rerun()

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
        st.markdown('<br><div class="reset-btn">', unsafe_allow_html=True)
        if st.button("Reset Match", key="reset"):
            st.session_state.started = False
            supabase.table("match_data").update({"runs":0, "balls":0, "target":0}).eq("id", 1).execute()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
