import streamlit as st
from supabase import create_client

# 1. DATABASE CONNECTION (Embedded as requested)
URL = "https://wkwxtnzdisclwbrygpez.supabase.co"
KEY = "sb_publishable_hQXQy84zDzyyT6Q2cvVIQA_6qqwY_uA"
supabase = create_client(URL, KEY)

# 2. DATA FUNCTIONS
def get_match():
    return supabase.table("match_data").select("*").eq("id", 1).single().execute().data

def update_score(run_val, ball_inc=1):
    d = get_match()
    supabase.table("match_data").update({
        "runs": d['runs'] + run_val, 
        "balls": d['balls'] + ball_inc
    }).eq("id", 1).execute()

def reset_match():
    supabase.table("match_data").update({
        "runs": 0, "balls": 0, "target": 0
    }).eq("id", 1).execute()

# 3. INTERFACE LOGIC
params = st.query_params
if params.get("mode") == "overlay":
    # --- CAMERA OVERLAY VIEW ---
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] { background-color: rgba(0,0,0,0); }
            .ticker {
                background: linear-gradient(90deg, #8bc34a 0%, #2e7d32 100%);
                color: white; padding: 12px 20px; border-radius: 12px;
                font-family: 'Arial Black', sans-serif; display: flex; 
                justify-content: space-between; align-items: center; width: 320px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            }
        </style>
    """, unsafe_allow_html=True)
    
    d = get_match()
    ov = f"{d['balls']//6}.{d['balls']%6}"
    
    st.markdown(f"""
        <div class="ticker">
            <div style="font-size: 30px;">{d['runs']} <span style="font-size:18px;">({ov})</span></div>
            <div style="font-size: 14px; text-align: right; line-height:1.2;">
                TGT: {d['target']}<br>MAX: {d['match_overs']} OV
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.rerun() 

else:
    # --- MOBILE CONTROLLER VIEW ---
    st.set_page_config(page_title="Cricket Scorer", layout="centered")
    data = get_match()
    
    # Simple Setup Section
    with st.expander("Match Settings (Overs/Target)"):
        new_target = st.number_input("Set Target", value=data['target'])
        if st.button("Update Target", use_container_width=True):
            supabase.table("match_data").update({"target": new_target}).eq("id", 1).execute()
            st.rerun()

    # Big Metrics for visibility
    c1, c2 = st.columns(2)
    c1.metric("SCORE", data['runs'])
    c2.metric("OVERS", f"{data['balls']//6}.{data['balls']%6}")

    # Scoring Grid (Large buttons for mobile)
    st.write("### Record Runs")
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    
    if r1_col1.button("0", use_container_width=True): update_score(0); st.rerun()
    if r1_col2.button("1", use_container_width=True): update_score(1); st.rerun()
    if r1_col3.button("2", use_container_width=True): update_score(2); st.rerun()
    if r2_col1.button("3", use_container_width=True): update_score(3); st.rerun()
    if r2_col2.button("4", use_container_width=True, type="primary"): update_score(4); st.rerun()
    if r2_col3.button("6", use_container_width=True, type="primary"): update_score(6); st.rerun()

    st.divider()

    # Extras with simple popover selection
    st.write("### Extras")
    ex1, ex2 = st.columns(2)
    
    with ex1:
        with st.popover("WIDE +", use_container_width=True):
            for r in range(7):
                if st.button(f"WD + {r}", key=f"wd{r}", use_container_width=True):
                    update_score(1 + r, ball_inc=0); st.rerun()
    with ex2:
        with st.popover("NO BALL +", use_container_width=True):
            for r in range(7):
                if st.button(f"NB + {r}", key=f"nb{r}", use_container_width=True):
                    update_score(1 + r, ball_inc=0); st.rerun()

    st.write("") 
    if st.button("🔄 Reset Match", type="secondary", use_container_width=True):
        reset_match(); st.rerun()

    # Overlay Link Helper
    st.markdown("---")
    st.write("🔗 **Overlay Link for Prism Live / CameraFi:**")
    # This automatically detects the current app URL
    base_url = st.get_option("browser.gatherUsageStats") 
    st.code(f"https://share.streamlit.io/YOUR_GITHUB_PATH/?mode=overlay")
    st.caption("Note: Replace the link above with your actual browser URL + '?mode=overlay'")
