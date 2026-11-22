import streamlit as st
import requests
import html
import time


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Language Translation Tool",
    page_icon="🌐",
    layout="wide"
)


# ==================================================
# LANGUAGE LIST
# ==================================================

LANGUAGES = {
    "English": "en",
    "Kannada": "kn",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Russian": "ru",
    "Portuguese": "pt",
    "Italian": "it",
    "Urdu": "ur"
}

LANGUAGE_NAMES = list(LANGUAGES.keys())


# ==================================================
# SESSION STATE
# ==================================================

if "source_language" not in st.session_state:
    st.session_state.source_language = "English"

if "target_language" not in st.session_state:
    st.session_state.target_language = "Kannada"

if "source_text" not in st.session_state:
    st.session_state.source_text = ""

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "translation_error" not in st.session_state:
    st.session_state.translation_error = ""


# ==================================================
# GOOGLE TRANSLATION
# ==================================================

def google_translate(text, source_code, target_code):

    url = "https://translate.googleapis.com/translate_a/single"

    params = {
        "client": "gtx",
        "sl": source_code,
        "tl": target_code,
        "dt": "t",
        "q": text
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    translated_parts = []

    for part in data[0]:
        if part and part[0]:
            translated_parts.append(part[0])

    translated_text = "".join(translated_parts).strip()

    if not translated_text:
        raise ValueError("Google returned an empty translation.")

    return translated_text


# ==================================================
# MYMEMORY FALLBACK
# ==================================================

def mymemory_translate(text, source_code, target_code):

    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"{source_code}|{target_code}"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    status = data.get("responseStatus")

    if status != 200:
        details = data.get(
            "responseDetails",
            "MyMemory translation failed."
        )

        raise ValueError(str(details))

    translated_text = data.get(
        "responseData",
        {}
    ).get(
        "translatedText",
        ""
    )

    translated_text = html.unescape(
        translated_text
    ).strip()

    if not translated_text:
        raise ValueError("MyMemory returned an empty translation.")

    return translated_text


# ==================================================
# TRANSLATION WITH FALLBACK
# ==================================================

def translate_text(text, source_code, target_code):

    errors = []

    # Try Google first
    try:
        result = google_translate(
            text,
            source_code,
            target_code
        )

        return result

    except Exception as error:
        errors.append(f"Google: {error}")

    # Try MyMemory if Google fails
    try:
        result = mymemory_translate(
            text,
            source_code,
            target_code
        )

        return result

    except Exception as error:
        errors.append(f"MyMemory: {error}")

    raise RuntimeError(
        "Both translation services failed. "
        + "Please wait and try again."
    )


# ==================================================
# SWAP LANGUAGES
# ==================================================

def swap_languages():

    source = st.session_state.source_language
    target = st.session_state.target_language

    st.session_state.source_language = target
    st.session_state.target_language = source

    st.session_state.translated_text = ""
    st.session_state.translation_error = ""


# ==================================================
# CLEAR TEXT
# ==================================================

def clear_text():

    st.session_state.source_text = ""
    st.session_state.translated_text = ""
    st.session_state.translation_error = ""


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    /* Main page background */
    .stApp {
        background-color: #f4f7fb !important;
    }

    /* Make all headings visible */
    .stApp h1,
    .stApp h2,
    .stApp h3 {
        color: #172033 !important;
        opacity: 1 !important;
    }

    /* Main title */
    h1 {
        text-align: center;
        font-weight: 700 !important;
    }

    /* Text and labels */
    .stApp p,
    .stApp label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p {
        color: #172033 !important;
        opacity: 1 !important;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #475569 !important;
        font-size: 17px;
        margin-bottom: 25px;
    }

    /* Text areas */
    div[data-testid="stTextArea"] textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        opacity: 1 !important;

        font-family:
            "Nirmala UI",
            "Noto Sans Kannada",
            "Arial Unicode MS",
            sans-serif !important;

        font-size: 19px !important;
        font-weight: 500 !important;
        line-height: 1.7 !important;
    }

    /* Disabled output box */
    div[data-testid="stTextArea"] textarea:disabled {
        background-color: #ffffff !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        opacity: 1 !important;
    }

    /* Dropdown text */
    div[data-testid="stSelectbox"] {
        color: #172033 !important;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
    }

    /* Translate button */
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# TITLE
# ==================================================

st.title("🌐 Language Translation Tool")

st.markdown(
    """
    <p class="subtitle">
        Translate text between different languages instantly
    </p>
    """,
    unsafe_allow_html=True
)


# ==================================================
# LANGUAGE SELECTION
# ==================================================

source_col, swap_col, target_col = st.columns(
    [5, 1, 5]
)

with source_col:

    st.selectbox(
        "Translate From",
        LANGUAGE_NAMES,
        key="source_language"
    )

with swap_col:

    st.write("")
    st.write("")

    st.button(
        "⇄",
        help="Swap source and target languages",
        use_container_width=True,
        on_click=swap_languages
    )

with target_col:

    st.selectbox(
        "Translate To",
        LANGUAGE_NAMES,
        key="target_language"
    )


# ==================================================
# INPUT AND OUTPUT BOXES
# ==================================================

left_col, right_col = st.columns(2)

with left_col:

    st.subheader("Enter Text")

    st.text_area(
        "Source Text",
        key="source_text",
        height=260,
        placeholder="Type or paste your text here...",
        label_visibility="collapsed"
    )

with right_col:

    st.subheader("Translated Text")

    st.text_area(
        "Translation Result",
        value=st.session_state.translated_text,
        height=260,
        placeholder="Your translation will appear here...",
        label_visibility="collapsed",
        disabled=True
    )


# ==================================================
# BUTTONS
# ==================================================

button_col1, button_col2 = st.columns(2)

with button_col1:

    translate_clicked = st.button(
        "🌐 Translate Now",
        type="primary",
        use_container_width=True
    )

with button_col2:

    st.button(
        "🗑️ Clear",
        use_container_width=True,
        on_click=clear_text
    )


# ==================================================
# TRANSLATION PROCESS
# ==================================================

if translate_clicked:

    input_text = st.session_state.source_text.strip()

    source_language = st.session_state.source_language
    target_language = st.session_state.target_language

    source_code = LANGUAGES[source_language]
    target_code = LANGUAGES[target_language]

    # Clear old result before a new translation
    st.session_state.translated_text = ""
    st.session_state.translation_error = ""

    if not input_text:

        st.warning("Please enter some text to translate.")

    elif source_language == target_language:

        st.session_state.translated_text = input_text
        st.rerun()

    else:

        try:

            with st.spinner("Translating your text..."):

                result = translate_text(
                    input_text,
                    source_code,
                    target_code
                )

                st.session_state.translated_text = result

            # Refresh so output appears in the right box
            st.rerun()

        except Exception as error:

            st.session_state.translation_error = str(error)

            st.error(
                "Translation service is temporarily unavailable."
            )

            st.info(
                "Please check your internet connection "
                "and try again in a little while."
            )


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#475569;
        font-size:14px;
    ">
        Built with Python and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)