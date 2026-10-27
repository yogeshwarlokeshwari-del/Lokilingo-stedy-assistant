from google import genai
from streamlit_mic_recorder import mic_recorder
import streamlit as st
import speech_recognition as sr
import os

# 1. Page Configuration
st.set_page_config(
    page_title="LokiLingo Study Assistant", page_icon="🤖", layout="centered"
)

st.title("🤖 LokiLingo - AI Study Assistant")
st.write(
    "Hello! I am your AI study assistant. Ask me anything, and feel free to"
    " change the language above if needed!"
)

# 2. Configure Gemini API (உங்கள் API கீ-யை இங்கு போடவும்)
API_KEY = "உங்கள்_Gemini_API_Key-யை_இங்கு_போடவும்"

# --- 3. மொழி மற்றும் கண்ட்ரோல்ஸ் பகுதி ---
col1, col2 = st.columns([2, 1])

with col1:
  selected_language = st.selectbox(
      "🌐 Select Language:",
      [
          "English",
          "Tamil (தமிழ்)",
          "Telugu (తెలుగు)",
          "Malayalam (മലയാളം)",
          "Kannada (ಕನ್ನಡ)",
          "Hindi (हिन्दी)",
      ],
  )

with col2:
  st.write("")
  st.write("")
  if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# குரல் பதிவு செய்யும் பட்டன்
audio_data = mic_recorder(
    start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", just_once=True, key="voice_btn"
)

# ஆடியோவை டெக்ஸ்டாக மாற்றும் பகுதி
spoken_text = ""
if audio_data:
  # mic_recorder தரும் ஆடியோ பைலை சேமித்து டெக்ஸ்டாக மாற்றுவது
  audio_bytes = audio_data["bytes"]
  audio_file_path = "temp_audio.wav"
  with open(audio_file_path, "wb") as f:
    f.write(audio_bytes)

  r = sr.Recognizer()
  try:
    with sr.AudioFile(audio_file_path) as source:
      audio_content = r.record(source)
      # செலக்ட் செய்த மொழிக்கு ஏற்ப குரலை டெக்ஸ்டாக மாற்றுவது (தமிழாக இருந்தால் ta-IN)
      lang_code = "ta-IN" if "Tamil" in selected_language else "en-US"
      spoken_text = r.recognize_google(audio_content, language=lang_code)
  except Exception as e:
    st.warning("Could not understand audio. Please try typing or speaking again.")
  finally:
    if os.path.exists(audio_file_path):
      os.remove(audio_file_path)

# 4. Main Chat Logic
if API_KEY == "உங்கள்_Gemini_API_Key-யை_இங்கு_போடவும்":
  st.warning("Please enter your actual Gemini API Key in the code!")
else:
  client = genai.Client(api_key=API_KEY)

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # --- 5. டைப்பிங் பார் அல்லது வாய்ஸ் டெக்ஸ்ட் ---
  user_query = st.chat_input("Type your question here...")

  # டைப் செய்தாலோ அல்லது வாய்ஸ் மூலமாக டெக்ஸ்ட் கிடைத்தாலோ இது வேலை செய்யும்
  final_query = user_query if user_query else spoken_text

  if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
      st.markdown(final_query)

    with st.chat_message("assistant"):
      with st.spinner("Thinking..."):
        try:
          system_instruction = f"""
                    You are LokiLingo, an intelligent and friendly AI study assistant. 
                    CRITICAL FOUNDER RULE: If anyone asks who your founder, creator, or developer is (in any language), you MUST explicitly state that your founder is Logeswar S (லோகேஷ்வர் எஸ்). 
                    You help 12th standard and other students with their studies.
                    CRITICAL LANGUAGE RULE: You MUST reply entirely in the following selected language: {selected_language}. (If English is selected, reply in English).
                    Explain complex concepts simply, accurately, and encourage the student warmly.
                    """

          response = client.models.generate_content(
              model="gemini-2.5-flash",
              contents=[
                  system_instruction,
                  *[
                      f"{m['role']}: {m['content']}"
                      for m in st.session_state.messages
                  ],
              ],
          )

          bot_reply = response.text
          st.markdown(bot_reply)

          st.session_state.messages.append(
              {"role": "assistant", "content": bot_reply}
          )
        except Exception as e:
          st.error(f"An error occurred: {e}")