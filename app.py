import streamlit as st
import json

from dotenv import load_dotenv
import os
import streamlit as st
import json
from groq import Groq
from dotenv import load_dotenv
import os
# Load env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Supplement Recommender", page_icon="💊", layout="wide")

# -------------------------------------------------------------
# TITLE
# -------------------------------------------------------------
st.title("💊 AI Supplement Recommendation System")
st.write("Enter your information and get a personalized, AI-generated supplement plan.")

# -------------------------------------------------------------
# USER INPUT FORM
# -------------------------------------------------------------
with st.form("user_form"):
    st.subheader("المعلومات الشخصية")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("العمر", 16, 80)
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        weight = st.number_input("الوزن (كلغ)", 30, 200)

    with col2:
        height = st.number_input("الطول (سم)", 120, 220)
        activity = st.selectbox("مستوى النشاط", [
            "خامل",
            "تمارين 1-2 مرات في الأسبوع",
            "تمارين 3 مرات أو أكثر في الأسبوع"
        ])
        sleep = st.number_input("عدد ساعات النوم في اليوم", 3, 12)

    st.subheader("الأهداف والصحة العامة")
    goal = st.multiselect("الأهداف الرئيسية", [
        "زيادة الكتلة العضلية",
        "خسارة الوزن",
        "تحسين النوم",
        "زيادة الطاقة",
        "تقوية المناعة"
    ])

    symptoms = st.multiselect("الأعراض الحالية", [
        "التعب",
        "التوتر",
        "تساقط الشعر",
        "ضعف المناعة",
        "تشنجات عضلية",
        "قلة الشهية"
    ])

    medical_flags = st.multiselect("الحالات الطبية", [
        "مشاكل في الكلى",
        "حامل / مرضعة"
    ])

    protein_intake = st.selectbox("مستوى استهلاك البروتين", [
        "منخفض",
        "متوسط",
        "مرتفع"
    ])

    submitted = st.form_submit_button("إنشاء توصية باستخدام الذكاء الاصطناعي")


# -------------------------------------------------------------
# ON SUBMIT → SEND TO AI
# -------------------------------------------------------------
if submitted:
    with st.spinner("Generating personalized supplement plan..."):

        user_profile = {
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "activity": activity,
            "goals": goal,
            "sleep": sleep,
            "symptoms": symptoms,
            "medical_flags": medical_flags,
            "protein_intake": protein_intake
        }

        prompt = f"""
You are a certified nutrition expert. 
You will generate a SAFE, evidence-based supplement plan. 
You MUST follow these rules:
- DO NOT give medical diagnosis
- DO NOT recommend illegal or unsafe substances
- Dosages must be safe and standard
- Always include food alternatives
- Always warn if the user has kidney issues, pregnancy, or breastfeeding

Generate recommendations for this user profile:

{json.dumps(user_profile, indent=2)}

Return ONLY valid JSON in this format:

{{
 "supplements": [
   {{
     "name": "",
     "name_en": "",
     "why": "",
     "dosage": "",
     "timing": "",
     "risks": ""
   }}
 ],
 "food_equivalents": [],
 "general_advice": ""
}}
in arabic language
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = response.choices[0].message.content

        # JSON PARSE
        try:
            data = json.loads(output)
        except:
            st.error("AI returned invalid JSON. Showing raw output:")
            st.text(output)
            st.stop()

    # -------------------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------------------
    st.success("Done! Here are your personalized recommendations:")
    st.divider()

    # Supplements
    st.subheader("Recommended Supplements 💡")
    for s in data["supplements"]:
        st.markdown(f"### {s['name']}")
        st.markdown(f"### {s['name_en']}")
        st.write(f"**Why:** {s['why']}")
        st.write(f"**Dosage:** {s['dosage']}")
        st.write(f"**Timing:** {s['timing']}")
        st.write(f"**Risks / Precautions:** {s['risks']}")
        st.divider()

    # Food equivalents
    st.subheader("Food Alternatives 🍽️")
    st.write(", ".join(data["food_equivalents"]))

    # General advice
    st.subheader("General Lifestyle Advice 🧠")
    st.write(data["general_advice"])
