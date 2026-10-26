import os
import asyncio
import streamlit as st
from google import genai
import edge_tts  # لتثبيتها: pip install edge-tts

# إعداد صفحة التطبيق
st.set_page_config(
    page_title="Tunisian AI Video Studio",
    page_icon="🎬",
    layout="wide"
)

# تخصيص التصميم
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #2b5876;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #4e4376;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Tunisian AI Video & Voice Studio")
st.markdown("منصة ذكية لصياغة المحتوى التونسي، التوليد الصوتي، وتحريك الشخصيات.")

# القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    api_key_input = st.text_input("مفتاح Google Gemini API", type="password")
    st.markdown("---")
    st.caption("ملاحظة: تأكد من تفعيل مفتاح صالح من Google AI Studio.")

# تهيئة الـ Session State
if "script_text" not in st.session_state:
    st.session_state["script_text"] = ""
if "audio_path" not in st.session_state:
    st.session_state["audio_path"] = None

col1, col2 = st.columns([1, 1], gap="large")

# ----------------- العمود الأول: السكريبت -----------------
with col1:
    st.subheader("1. 📝 صياغة السكريبت (بالدارجة التونسية)")
    topic = st.text_area("علاش يحكي الفيديو؟", placeholder="مثلاً: 3 نصائح لأصحاب المشاريع الصغيرة في تونس...")
    target_duration = st.selectbox("مدة الفيديو", ["قصير (Reels/TikTok)", "متوسط (دقيقة)", "طويل (+دقيقة)"])
    
    if st.button("توليد السكريبت التونسي 🚀"):
        if not api_key_input:
            st.error("الرجاء إدخال مفتاح Gemini API في القائمة الجانبية أولاً.")
        elif not topic.strip():
            st.warning("الرجاء كتابة موضوع الفيديو.")
        else:
            try:
                client = genai.Client(api_key=api_key_input)
                prompt_text = f"""
                Act as an expert Tunisian content creator and copywriter.
                Write an engaging, natural, and persuasive video script in pure Tunisian Arabic (الدارجة التونسية) based on this topic: "{topic}".
                The target video format is: {target_duration}.
                Structure:
                - Strong Hook (البداية تجذب الانتباه مباشرة)
                - Value / Story (صلب الموضوع بدون تعقيد)
                - CTA (دعوة واضحة للتفاعل في النهاية)
                Output ONLY the spoken script without brackets, speaker tags, or scene directions.
                """
                with st.spinner("جاري صياغة السكريبت..."):
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_text
                    )
                    st.session_state["script_text"] = response.text.strip()
                    st.success("تم توليد السكريبت بنجاح! ✅")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Gemini API: {e}")

    # حقل التعديل يربط مباشرة مع session_state
    final_script = st.text_area(
        "مراجعة وتعديل السكريبت:", 
        value=st.session_state["script_text"], 
        height=180,
        key="editable_script_box"
    )
    # تحديث النص الفعلي عند تعديله
    st.session_state["script_text"] = final_script

# ----------------- دالة توليد الصوت (Edge TTS) -----------------
async def generate_speech(text: str, voice: str, output_file: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# ----------------- العمود الثاني: الصوت والفيديو -----------------
with col2:
    st.subheader("2. 🎙️ الصوت وتحريك الوجه (Lip-Sync)")
    
    uploaded_image = st.file_uploader("حمّل صورة الأفاتار (Portrait)", type=["jpg", "png", "jpeg"])
    
    # أصوات عربية طبيعية مدعومة عبر edge-tts
    voice_option = st.selectbox(
        "اختر نبرة الصوت",
        [
            ("تونسي - Hedi (رجالي)", "ar-TN-HediNeural"),
            ("تونسي - Reem (نسائي)", "ar-TN-ReemNeural")
        ],
        format_func=lambda x: x[0]
    )
    
    generate_media_btn = st.button("إنتاج الصوت 🎬")

    if generate_media_btn:
        if not st.session_state["script_text"].strip():
            st.warning("الرجاء توليد أو كتابة سكريبت أولاً.")
        else:
            with st.spinner("جاري توليد الملف الصوتي..."):
                output_audio = "generated_voice.mp3"
                selected_voice_code = voice_option[1]
                
                try:
                    asyncio.run(generate_speech(st.session_state["script_text"], selected_voice_code, output_audio))
                    st.session_state["audio_path"] = output_audio
                    st.success("تم توليد الصوت بنجاح! 🎧")
                except Exception as err:
                    st.error(f"حدث خطأ أثناء توليد الصوت: {err}")

    # عرض مشغل الصوت إذا تم توليده
    if st.session_state["audio_path"] and os.path.exists(st.session_state["audio_path"]):
        st.audio(st.session_state["audio_path"], format="audio/mp3")

    # جزء الـ Lip-Sync
    if uploaded_image and st.session_state["audio_path"]:
        st.divider()
        st.markdown("**3. تحريك الصورة مع الصوت (Lip-Sync Video)**")
        if st.button("توليد الفيديو النهائي (SadTalker / LivePortrait) 🎥"):
            st.info("""
            لإتمام هذه الخطوة سحابياً:
            يمكنك ربط هذا الزر بـ **Replicate API** عبر نموذج `cjwbw/sadtalker` وتمرير الصورة والملف الصوتي ليعود لك برابط فيديو جاهز ومباشر.
            """)