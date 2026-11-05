import streamlit as st
import datetime
import pandas as pd
import math

# Mobile-friendly page configuration
st.set_page_config(page_title="FloraFlex Master Log", page_icon="🌿", layout="centered")

st.title("🌿 FloraFlex Master Grow Log")
st.caption("Complete Seed-to-Harvest Crop Steering & Measuring Spoon Assistant")

# --- INITIALIZING BASELINE SYSTEM VALUES ---
st.sidebar.header("🎯 System Baseline Constraints")
st.sidebar.markdown("""
- **Medium:** Coco-Perlite-Biochar Blend
- **Pots:** 3-Gallon Plastic FloraFlex Rounds
- **System:** Automated Drain-to-Waste (No Sitting Runoff)
- **Tap Water Baseline:** ~300 PPM (High Calcium / Low Mg)
- **Silica Policy:** NONE (During Veg/Stretch) -> Dynamic in Bloom
- **Reservoir Rule:** Air-Stone OFF (Circulation Pump ONLY)
""")

# --- TAB SETUP ---
tab1, tab2, tab3 = st.tabs(["📝 Log Today's Run", "🧪 Reservoir Mixer", "📅 Full-Cycle Schedule"])

# --- TAB 1: DAILY RUNOFF, ENVIRONMENT & LIGHT LOGGER ---
with tab1:
    st.subheader("🕒 Runoff Data Entry")
    
    date_today = st.date_input("Log Date", datetime.date.today())
    feed_time = st.selectbox("Feed Cycle", ["6:00 AM (Heavy automated flush + VGNX hand-pour)", "3:00 PM (Lighter automated top-off)"])
    
    col_run1, col_run2 = st.columns(2)
    with col_run1:
        st.markdown("**📥 Input Targets**")
        input_ppm = st.number_input("Measured Input PPM", min_value=0, max_value=2000, value=730, step=10)
        input_ph = st.number_input("Measured Input pH", min_value=0.0, max_value=14.0, value=5.8, step=0.05)
    with col_run2:
        st.markdown("**📤 Runoff Metrics**")
        runoff_ppm = st.number_input("Measured Runoff PPM", min_value=0, max_value=2000, value=641, step=10)
        runoff_ph = st.number_input("Measured Runoff pH", min_value=0.0, max_value=14.0, value=6.2, step=0.05)

    st.markdown("---")
    st.subheader("🌡️ Environment & Lighting Parameters")
    
    col_env1, col_env2 = st.columns(2)
    with col_env1:
        st.markdown("**🌤️ Room Air Climate**")
        room_temp = st.number_input("Room Temperature (°F)", min_value=50.0, max_value=110.0, value=79.0, step=0.5)
        room_rh = st.number_input("Relative Humidity (%)", min_value=10.0, max_value=100.0, value=71.0, step=1.0)
    with col_env2:
        st.markdown("**💡 VIVOSUN VSFL6450 Controls**")
        light_intensity = st.slider("Dimmer Intensity (%)", min_value=0, max_value=100, value=57)
        light_distance = st.number_input("Hanging Distance (Inches)", min_value=1, max_value=50, value=19, step=1)
        light_cycle = st.selectbox("Current Phase / Photoperiod", [
            "Late Veg / Transition (18/6)", 
            "Early Flower Weeks 1-3 (12/12 Stretch)", 
            "Mid Flower Weeks 4-5 (12/12 Bulking)", 
            "Late Flower Weeks 6-8 (12/12 Ripening)", 
            "Final Flush Week 9+ (12/12 or 10/14)"
        ])

    st.markdown("---")
    st.subheader("🌿 Canopy Observations")
    canopy_status = st.multiselect(
        "Plant Posture & Development", 
        ["Praying (Optimal Transpiration)", "Flat/Stagnant", "Drooping (Over/Under-Watered)", "Deepening Green (Chlorophyll Saturation)", "Pale/Yellow Tips (Lockout Signs)", "ScROG Net Tucked/Filled", "Pistils Popping", "Trichomes Clouding / Amber Taper"],
        default=["Praying (Optimal Transpiration)", "Deepening Green (Chlorophyll Saturation)"]
    )
    notes = st.text_input("Daily Notes (e.g., Flip tracking, uniform green progress check)")

    # --- MATH ENGINES (VPD & WATER RUNOFF CALCULATIONS) ---
    temp_c = (room_temp - 32) * 5 / 9
    svp = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    avp = svp * (room_rh / 100.0)
    leaf_temp_c = ((room_temp - 2.0) - 32) * 5 / 9
    svp_leaf = 0.61078 * math.exp((17.27 * leaf_temp_c) / (leaf_temp_c + 237.3))
    calculated_vpd = max(0.0, svp_leaf - avp)

    tap_ppm_baseline = 300
    true_nutrient_ppm = max(0, input_ppm - tap_ppm_baseline)
    drawdown = input_ppm - runoff_ppm
    ph_drift = runoff_ph - input_ph

    st.markdown("---")
    st.subheader("🤖 AI Steering Diagnostics")
    
    # 1. Environment / VPD Diagnostics
    st.markdown(f"📊 **Calculated Canopy VPD:** `{round(calculated_vpd, 2)} kPa`")
    if "Late Veg" in light_cycle and (0.8 <= calculated_vpd <= 1.05):
        st.success("🟢 **Veg VPD Sweet Spot:** Optimal vegetative transpiration rate. Stomata are open and active.")
    elif "Flower" in light_cycle and (1.1 <= calculated_vpd <= 1.4):
        st.success("🟢 **Flower VPD Sweet Spot:** Perfect mid-to-late flower environment. Higher VPD allows massive flower stack transpiration safely.")
    elif calculated_vpd < 0.8:
        st.warning("⚠️ **VPD Too Low:** Air is humid or cool. Plant transpiration slows down, reducing mineral travel speeds down stems.")
    else:
        st.error("🔴 **VPD Too High:** Air is too dry or hot. Leaves are losing water too fast, increasing tip burn risk.")

    # 2. Nutrient Diagnostics
    st.info(f"ℹ️ **Water Profile:** Out of your {input_ppm} total input PPM, **{true_nutrient_ppm} PPM** consists of active plant nutrients. The remaining 300 PPM is your source tap water.")
    
    if "Flush" in light_cycle:
        if runoff_ppm < 450:
            st.success(f"🟢 **Successful Leach:** Runoff is down to {runoff_ppm} PPM. Plant is smoothly consuming its stored tissue resources.")
        else:
            st.warning(f"⚠️ **Clearing Buffer:** Runoff is still at {runoff_ppm} PPM. Keep pouring straight low-PPM water to flush coco clean.")
    else:
        if drawdown > 90:
            st.success(f"🟢 **Aggressive Feeding:** Substrate drawdown is **{drawdown} PPM**. The plants are emptying the pantry. You have a green light to step up input by +50 PPM if canopy greening is uniform.")
        elif drawdown < 0:
            st.error(f"🔴 **Salt Stacking Warning:** Runoff is **{abs(drawdown)} PPM HIGHER** than input! Background tap minerals or fertilizer salts are accumulating. **Action:** Maintain current nutrient strength but increase the 6:00 AM automated flush volume by 10% to reset the core.")
        else:
            st.info(f"🔵 **Steady Baseline Uptake:** Drawdown is **{drawdown} PPM**. Root zone is balanced and safely cruising.")

    # 3. pH Buffer Diagnostics
    if 0.3 <= ph_drift <= 0.5:
        st.success(f"🟢 **Optimal Root Zone Buffer:** pH drifted perfectly from {input_ph} to {runoff_ph} (+{round(ph_drift,2)}). Magnesium and Phosphorus availability are maximized.")
    elif ph_drift > 0.5:
        st.warning(f"⚠️ **High pH Drift (+{round(ph_drift,2)}):** Runoff at {runoff_ph} is creeping up. High-calcium tap water can push coco buffers upward over time. Monitor closely.")
    else:
        st.error(f"🔴 **Stagnant pH Rise (+{round(ph_drift,2)}):** Core buffer might be getting oversaturated or stale. Check that drain lines are flowing freely.")

    if st.button("Save Entry To Log File"):
        st.toast("Data logged successfully!")

# --- TAB 2: RESERVOIR BATCH MIXER ---
with tab2:
    st.subheader("🧪 Measuring Spoon & Liquid Syringe Guide")
    st.markdown("Enter your total daily reservoir volume to calculate your strict water treatment ratios.")
    
    # Volume selector
    unit = st.radio("Choose Volume Unit:", ["Liters", "Gallons"], index=0)
    total_volume = st.number_input(f"Total Water Volume to Mix:", min_value=1.0, max_value=200.0, value=15.0, step=1.0)
    
    if unit == "Liters":
        gallons_total = total_volume / 3.78541
        liters_total = total_volume
    else:
        gallons_total = total_volume
        liters_total = total_volume * 3.78541

    st.markdown("---")
    st.markdown("### 📋 Morning Reservoir Recipe")
    
    # Calculating total teaspoons of Jack's (approx 0.82 tsp per gallon yields ~730 ppm target)
    total_tsps = gallons_total * 0.82
    tbsp_count = int(total_tsps // 3)
    remaining_tsps = round(total_tsps % 3, 2)
    
    if tbsp_count > 0:
        spoon_display = f"{tbsp_count} level Tbsp + {remaining_tsps} level tsp"
    else:
        spoon_display = f"{remaining_tsps} level tsp"

    # Frosty Nugs calculation (0.5 mL per Liter)
    total_frosty_nugs_ml = liters_total * 0.5

    col_mix1, col_mix2 = st.columns(2)
    with col_mix1:
        st.metric(label="Jack's 15-5-20 Spoon Amount", value=spoon_display)
        st.caption(f"Calculated to reach your target baseline over your 300 PPM tap.")
    with col_mix2:
        st.metric(label="Frosty Nugs (Magnesium)", value=f"{round(total_frosty_nugs_ml, 1)} mL")
        st.caption("Syringe dose calculated at 0.5 mL per Liter to balance your tap water's calcium profile.")

    st.markdown("---")
    st.markdown("### 🪣 Hand-Feeding Component")
    use_vgnx = st.checkbox("Include VGNX Exotic Blend hand-feed for this mix?", value=True)
    
    if use_vgnx:
        st.info("💡 **VGNX Exotic Blend Instructions:** Measure exactly **1/8 tsp** of powder, thoroughly mix it directly inside **2 Liters** dipped out of your main automated nutrient reservoir, and hand-pour over the pots immediately after the 6:00 AM cycle finishes.")
    else:
        st.warning("⏭️ **VGNX Skipped for this batch.** No hand-pour required today. Only run your standard automated line.")

    st.markdown("---")
    st.markdown("### ⏱️ Automated Cycle Distribution")
    st.markdown(f"To hitting your drainage target using your **{round(liters_total, 1)}L** batch:")
    st.write(f"🔹 **6:00 AM Heavy Flush (65% Volume):** ~{round(liters_total * 0.65, 1)} Liters")
    st.write(f"🔸 **3:00 PM Lighter Top-off (35% Volume):** ~{round(liters_total * 0.35, 1)} Liters")

# --- TAB 3: COMPLETE LIFECYCLE REFERENCE MATRIX ---
with tab3:
    st.subheader("📅 Full Seed-to-Harvest Reference Schedule")
    schedule_data = {
        "Growth Phase & Weeks": [
            "Late Veg (Current)", 
            "Flower Weeks 1-2 (Stretch)", 
            "Flower Week 3 (Budset)",
            "Flower Weeks 4-5 (Bulking)",
            "Flower Weeks 6-7 (Hardening)",
#Use code with caution.
"Flower Week 8 (Ripening)",
"Flower Week 9+ (Final Flush)"
],
"Target Input PPM": ["700-750", "750-820", "800-850", "850-900", "800-850", "600-650", "300 (Tap Only)"],
"Target Input pH": ["5.7-5.8", "5.8-5.9", "5.8-5.9", "5.8-5.9", "5.8-5.9", "5.9-6.0", "6.0-6.2"],
"Target Runoff PPM": ["620-660", "680-740", "750-800", "800-850", "750-800", "550-600", "< 400"],
"Target Runoff pH": ["6.2-6.3", "6.1-6.3", "6.0-6.2", "6.0-6.2", "6.1-6.3", "6.2-6.4", "6.3-6.5"],
"Target Canopy VPD": ["0.9 - 1.0 kPa", "1.0 - 1.1 kPa", "1.1 - 1.2 kPa", "1.2 - 1.3 kPa", "1.3 - 1.4 kPa", "1.3 - 1.4 kPa", "1.1 - 1.3 kPa"]
}
df = pd.DataFrame(schedule_data)
st.dataframe(df, hide_index=True)
