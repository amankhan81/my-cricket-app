import streamlit as st
from supabase import create_client
import json

# --- DB CONNECTION ---
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# --- DATA HELPERS ---
def get_match():
    try:
        return supabase.table("match_data").select("*").eq("id", 1).single().execute().data
    except:
        return {"runs": 0, "balls": 0, "match_overs": 8, "target": 0}

def update_db(runs_inc, balls_inc):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + runs_inc,
        "balls": d['balls'] + balls_inc
    }).eq("id", 1).execute()

# --- APP LOGIC ---
params = st.query_params

# 1. DATA API (Hidden - Fixes the Overlay Update issue)
if params.get("mode") == "data":
    st.write(json.dumps(get_match()))
    st.stop()

# 2. OVERLAY TICKER (No-Blink & Transparent)
elif params.get("mode") == "overlay":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"] { background: transparent !important; }
            header, footer, #MainMenu {display: none !important;}
            .ticker {
                position: fixed; top: 10px; left: 10px;
                background: #1B5E20; color: white; padding: 12px;
                border-radius: 8px; font-family: sans-serif; min-width: 200px;
            }
            .runs { font-size: 32px; font-weight: 900; }
            .target { background: black; padding: 4px 10px; border-radius: 0 0 5px 5px; font-size: 14px; }
        </style>
        <div class="ticker">
            <div id="lbl" style="font-size:10px;">1ST INNINGS</div>
            <div class="runs"><span id="r">0</span> <small id="ov" style="font-size:16px;">(0.0)</small></div>
            <div id="t_box" class="target" style="display:none;">Target <span id="t">0</span></div>
        </div>
        <script>
            async function up() {
                const res = await fetch(window.location.origin + window.location.pathname + '?mode=data');
                const d = await res.json();
                document.getElementById('r').innerText = d.runs;
                document.getElementById('ov').innerText = "(" + Math.floor(d.balls/6) + "." + (d.balls%6) + ")";
                if(d.target > 0) { document.getElementById('t_box').style.display='block'; document.getElementById('t').innerText=d.target; }
            }
            setInterval(up, 2000); up();
        </script>
    """, unsafe_allow_html=True)

# 3. MOBILE SCORER (Exact Image Redesign)
else:
    st.markdown(f"""
        <style>
            /* Background Color */
            .stApp {{ background-color: #FEE49B !important; }}
            
            /* Header Styling */
            .header-container {{ display: flex; justify-content: space-around; padding: 20px 0; font-family: sans-serif; }}
            .label {{ color: #4A90E2; font-size: 30px; font-weight: bold; text-shadow: 1px 1px white; }}
            .value {{ color: black; font-size: 70px; font-weight: 900; display: block; margin-top: -10px; }}

            /* Fixed 3-Column Grid for Mobile */
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                padding: 10px;
            }}
            .grid-item {{
                height: 100px; border-radius: 5px; display: flex;
                align-items: center; justify-content: center;
                font-size: 35px; font-weight: bold; cursor: pointer; border: none;
            }}
            .blue-btn {{ background-color: #A3C1E8; color: black; }}
            .green-btn {{ background-color: #00B050; color: black; }}
            .darkblue-btn {{ background-color: #0070C0; color: black; }}
            .undo-btn {{ background-color: #F8B195; color: black; font-size: 20px; }}

            /* Extras Styling */
            .extra-section {{ background-color: #C65911; color: white; text-align: center; font-size: 25px; font-weight: bold; padding: 8px; margin: 15px 0 5px 0; }}
            .extra-row {{ display: flex; gap: 5px; padding: 0 5px; }}
            .extra-item {{ flex: 1; background: #A3C1E8; height: 50px; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 1px solid #777; color: black; }}
        </style>
    """, unsafe_allow_html=True)

    d = get_match()

    # Score Display
    st.markdown(f"""
        <div class="header-container">
            <div style="text-align:center;"><span class="label">SCORE</span><span class="value">{d['runs']}</span></div>
            <div style="text-align:center;"><span class="label">OVERS</span><span class="value">{d['balls']//6}.{d['balls']%6}</span></div>
        </div>
    """, unsafe_allow_html=True)

    # Scoring Grid
    col1, col2, col3 = st.columns(3)
    if col1.button("1", use_container_width=True): update_db(1, 1); st.rerun()
    if col2.button("2", use_container_width=True): update_db(2, 1); st.rerun()
    if col3.button("3", use_container_width=True): update_db(3, 1); st.rerun()

    col4, col5, col6 = st.columns(3)
    with col4: st.markdown('<div class="green-btn">', unsafe_allow_html=True)
    if col4.button("4", use_container_width=True): update_db(4, 1); st.rerun()
    with col5: st.markdown('<div class="darkblue-btn">', unsafe_allow_html=True)
    if col5.button("6", use_container_width=True): update_db(6, 1); st.rerun()
    with col6: st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if col6.button("UNDO", use_container_width=True): 
        update_db(0, 0) # Placeholder for Undo Logic
        st.rerun()

    # Wides Bar
    st.markdown('<div class="extra-section">Wides</div>', unsafe_allow_html=True)
    w_cols = st.columns(5)
    for i in range(5):
        if w_cols[i].button(f"W+{i}", use_container_width=True):
            update_db(1 + i, 0); st.rerun()

    # No Ball Bar
    st.markdown('<div class="extra-section">No Ball</div>', unsafe_allow_html=True)
    n_cols = st.columns(7)
    for i in range(7):
        if n_cols[i].button(f"N+{i}", use_container_width=True):
            update_db(1 + i, 0); st.rerun()

    # Setup Footer
    with st.expander("⚙️ Setup"):
        st.write(f"Overlay Link: `https://score-easy.streamlit.app/?mode=overlay`")
        if st.button("RESET MATCH"):
            supabase.table("match_data").update({"runs": 0, "balls": 0, "target": 0}).eq("id", 1).execute()
            st.rerun()
