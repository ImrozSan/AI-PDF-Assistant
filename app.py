import streamlit as st
from pypdf import PdfReader
import re
from collections import Counter
import pandas as pd
import json
from ai import ask_ai 

# Try loading spaCy for NER analytics with fallback handling
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# --- Session State Initializations ---
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_pages" not in st.session_state:
    st.session_state.pdf_pages = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "points" not in st.session_state:
    st.session_state.points = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page_count" not in st.session_state:
    st.session_state.page_count = 0
if "word_count" not in st.session_state:
    st.session_state.word_count = 0
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

st.set_page_config(
    page_title="Enterprise AI PDF Intelligence Suite",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .insight-box {
        background: #1E293B;
        border-left: 5px solid #38BDF8;
        color: #F8FAFC;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    .insight-box h3 {
        color: #38BDF8 !important;
        margin-top: 0;
        font-weight: 700;
    }
    .insight-box p {
        color: #E2E8F0 !important;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 20px;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        background: linear-gradient(135deg, #2563EB 0%, #0891B2 100%);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-weight: 800; font-size: 2.8rem; margin-bottom: 0;'>🧠 AI PDF Intelligence Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.2rem; margin-top: 8px; font-weight: 400;'>Upload • Summarize • Analyze • Practice</p>", unsafe_allow_html=True)
st.divider()

# --- Sidebar Component ---
with st.sidebar:
    st.markdown("### 📥 Document Control Center")
    pdf = st.file_uploader("Upload Target PDF", type=["pdf"], label_visibility="collapsed")
    
    if pdf is not None:
        if st.session_state.pdf_text == "" or st.session_state.get("current_pdf_name") != pdf.name:
            with st.spinner("Extracting structural data & page grounding..."):
                reader = PdfReader(pdf)
                extracted_text = ""
                pages_list = []
                
                # Page Grounding logic: Tagging each page number explicitly
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- [PAGE {idx + 1}] ---\n" + page_text
                        pages_list.append({"page": idx + 1, "text": page_text})
                
                st.session_state.pdf_text = extracted_text
                st.session_state.pdf_pages = pages_list
                st.session_state.page_count = len(reader.pages)
                st.session_state.word_count = len(extracted_text.split())
                st.session_state.current_pdf_name = pdf.name
                st.session_state.quiz_data = None
                
        st.success("✅ Document Loaded Successfully")
        st.markdown("---")
        st.markdown("### 📊 Document Metadata")
        c1, c2 = st.columns(2)
        c1.metric("Total Pages", st.session_state.page_count)
        c2.metric("Word Count", f"{st.session_state.word_count:,}")
    else:
        st.session_state.pdf_text = ""
        st.session_state.pdf_pages = []
        st.session_state.chat_history = []
        st.session_state.summary = ""
        st.session_state.points = ""
        st.session_state.quiz_data = None
        st.info("Please upload a PDF document to begin analysis.")

# --- Main App Modules ---
if st.session_state.pdf_text:
    # UPDATED: 4 Dedicated Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Interactive Chat & Sources", 
        "📝 Automated Summaries",
        "📊 Visual & Entity Analytics",
        "🎯 Practice Quiz & Flashcards"
    ])
    
    # --- TAB 1: Chat with Page Citations ---
    with tab1:
        st.markdown("### Ask Questions About Your Document")
        
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])
        
        with st.form(key="chat_form", clear_on_submit=True):
            question = st.text_input("Enter your question based on document contents...", placeholder="e.g., Explain socket classes with page reference?")
            submit_button = st.form_submit_button(label="Send Question")
            
        if submit_button and question:
            with st.chat_message("user"):
                st.write(question)
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing document with Page Citations..."):
                    try:
                        # Prompt instructions for grounded source citations
                        prompt = (
                            f"Answer the user's question strictly using the provided PDF context below.\n"
                            f"IMPORTANT: At the end of your answer, explicitly mention the Page Number(s) "
                            f"(e.g. '📍 Source Citation: Page X') from where you retrieved the information.\n\n"
                            f"Question: {question}\n\nContext:\n{st.session_state.pdf_text[:12000]}"
                        )
                        reply = ask_ai(st.session_state.pdf_text, prompt)
                        st.write(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"⚠️ AI Engine Error: {e}")

    # --- TAB 2: Summaries & Takeaways ---
    with tab2:
        st.markdown("### Document Synthesis Engines")
        col_left, col_right = st.columns(2)
        
        with col_left:
            if st.button("Generate Executive Summary"):
                with st.spinner("Synthesizing text layers..."):
                    try:
                        st.session_state.summary = ask_ai(
                            st.session_state.pdf_text,
                            "Summarize this PDF in simple English across 5-6 cohesive sentences."
                        )
                    except Exception as e:
                        st.error(f"Summary Error: {e}")
                        
        with col_right:
            if st.button("Extract Key Breakthrough Points"):
                with st.spinner("Isolating critical data nodes..."):
                    try:
                        st.session_state.points = ask_ai(
                            st.session_state.pdf_text,
                            "Extract the 5 most critical core takeaways from this document in clear, high-impact bullet points."
                        )
                    except Exception as e:
                        st.error(f"Points Error: {e}")
        
        if st.session_state.summary:
            st.markdown(f"""
            <div class="insight-box">
                <h3>Executive Summary</h3>
                <p style="line-height: 1.6;">{st.session_state.summary}</p>
            </div>
            """, unsafe_allow_html=True)
            
        if st.session_state.points:
            st.markdown("""<div class="insight-box"><h3>Key Strategic Takeaways</h3>""", unsafe_allow_html=True)
            st.write(st.session_state.points)
            st.markdown("""</div>""", unsafe_allow_html=True)
            
        if st.session_state.summary or st.session_state.points:
            st.markdown("---")
            st.markdown("### 💾 Export Generated Insights")
            
            report_text = f"AI DOCUMENT INTELLIGENCE REPORT\n"
            report_text += f"Source Document: {st.session_state.get('current_pdf_name', 'Unknown')}\n"
            report_text += f"=========================================\n\n"
            if st.session_state.summary:
                report_text += f"EXECUTIVE SUMMARY:\n{st.session_state.summary}\n\n"
            if st.session_state.points:
                report_text += f"KEY TAKEAWAYS:\n{st.session_state.points}\n"
                
            st.download_button(
                label="📥 Download Executive Briefing (.txt)",
                data=report_text,
                file_name="AI_Document_Summary.txt",
                mime="text/plain"
            )

    # --- TAB 3: Visual Analytics & NER Entities ---
    with tab3:
        st.markdown("### 📊 Text Distribution & Key Themes")
        st.write("This section parses data metrics from the raw document string to discover core density clusters.")
        
        metric_col1, metric_col2 = st.columns(2)
        
        processed_words = re.findall(r'\b\w{5,}\b', st.session_state.pdf_text.lower())
        top_words = Counter(processed_words).most_common(12)
        
        with metric_col1:
            reading_time_mins = max(1, round(st.session_state.word_count / 238))
            st.metric("⏳ Estimated Document Reading Time", f"{reading_time_mins} Min")
            st.write("")
            st.write("**Top High-Frequency Context Terms Table**")
            if top_words:
                df_table = pd.DataFrame(top_words, columns=['Significant Term', 'Frequency Density'])
                st.dataframe(df_table, use_container_width=True, hide_index=True)
            else:
                st.info("Insufficient textual structure to parse keywords.")
                
        with metric_col2:
            st.write("**Top Vocabulary Density Clusters**")
            if top_words:
                df_chart = pd.DataFrame(top_words, columns=['Word', 'Occurrences'])
                st.bar_chart(data=df_chart, x='Word', y='Occurrences', color='#3B82F6')
            else:
                st.info("Insufficient text data to populate keyword density histograms.")
                
        st.markdown("---")
        # FEATURE 2: Named Entity Recognition (NER)
        st.markdown("### 🏷️ Intelligent Entity Recognition (NER)")
        if nlp:
            with st.spinner("Extracting domain entities using spaCy NLP..."):
                doc = nlp(st.session_state.pdf_text[:8000]) # performance sample limit
                
                orgs = set([ent.text.strip() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]])
                concepts = set([ent.text.strip() for ent in doc.ents if ent.label_ in ["GPE", "DATE", "LAW", "NORP"]])
                
                c_ner1, c_ner2 = st.columns(2)
                with c_ner1:
                    st.write("**🏢 Key Organizations, Libraries & Systems**")
                    if orgs:
                        st.write(", ".join([f"`{item}`" for item in list(orgs)[:12]]))
                    else:
                        st.caption("No explicit organization entities discovered.")
                
                with c_ner2:
                    st.write("**🌐 Key Standards, Dates & Protocols**")
                    if concepts:
                        st.write(", ".join([f"`{item}`" for item in list(concepts)[:12]]))
                    else:
                        st.caption("No specific protocols/dates discovered.")
        else:
            st.info("💡 Tip: Install `spacy` and run `python -m spacy download en_core_web_sm` to enable real-time Entity Recognition.")

   # --- TAB 4: FEATURE 3 - Auto-Quiz & Flashcards ---
    with tab4:
        st.markdown("### 🎯 AI Auto-Generated Quiz & Flashcards")
        st.write("Generate custom practice questions and definition cards directly from document topics.")
        
        if st.button("⚡ Generate Interactive Practice Quiz"):
            with st.spinner("Generating MCQs and Flashcards..."):
                try:
                    quiz_prompt = (
                        "Generate 3 Multiple Choice Questions (MCQs) and 2 Flashcard Key Terms from this document text.\n"
                        "Respond STRICTLY in valid JSON format only, with no backticks, no markdown formatting, and no conversational text.\n"
                        "JSON Format Structure:\n"
                        "{\n"
                        '  "mcqs": [\n'
                        '    {"question": "Q text", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A", "explanation": "Brief explanation"}\n'
                        '  ],\n'
                        '  "flashcards": [\n'
                        '    {"term": "Term Name", "definition": "Term Definition"}\n'
                        '  ]\n'
                        "}\n\n"
                        f"Document Text:\n{st.session_state.pdf_text[:5000]}"
                    )
                    
                    raw_response = ask_ai(st.session_state.pdf_text, quiz_prompt)
                    
                    # Regex to extract purely the JSON object
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    
                    if json_match:
                        clean_json = json_match.group(0)
                        st.session_state.quiz_data = json.loads(clean_json)
                        st.success("✅ Quiz Generated Successfully!")
                    else:
                        st.error("⚠️ AI response did not contain a valid JSON object.")
                        st.code(raw_response)

                except Exception as e:
                    st.error(f"Quiz Generation Error: {e}")
                    
        # --- RENDER QUIZ & FLASHCARDS ---
        if st.session_state.quiz_data:
            q_data = st.session_state.quiz_data
            
            # Flexible key fetching (handles variations in AI response)
            mcqs = q_data.get("mcqs") or q_data.get("MCQs") or q_data.get("questions") or []
            cards = q_data.get("flashcards") or q_data.get("Flashcards") or q_data.get("cards") or []
            
            q_tab1, q_tab2 = st.tabs(["📝 Multiple Choice Questions", "🎴 Study Flashcards"])
            
            # TAB 1: MCQs
            with q_tab1:
                if mcqs:
                    for idx, q in enumerate(mcqs):
                        st.markdown(f"**Q{idx+1}: {q.get('question', 'Question Text Missing')}**")
                        
                        options = q.get("options", ["Option A", "Option B"])
                        user_ans = st.radio("Choose Option:", options, key=f"q_radio_{idx}")
                        
                        if st.button(f"Verify Answer #{idx+1}", key=f"q_btn_{idx}"):
                            correct_ans = q.get("answer", "")
                            if user_ans == correct_ans:
                                st.success("✅ Correct Answer!")
                            else:
                                st.error(f"❌ Incorrect. Correct answer is: **{correct_ans}**")
                            st.info(f"💡 Explanation: {q.get('explanation', 'No explanation provided.')}")
                        st.divider()
                else:
                    st.warning("⚠️ No MCQs found in the generated response. Please try clicking generate again.")

            # TAB 2: Flashcards
            with q_tab2:
                if cards:
                    cols = st.columns(len(cards) if len(cards) > 0 else 1)
                    for idx, card in enumerate(cards):
                        with cols[idx % len(cols)]:
                            term_name = card.get('term') or card.get('key_term') or f"Key Term {idx+1}"
                            definition = card.get('definition') or card.get('meaning') or "No definition available."
                            
                            with st.expander(f"🔑 **{term_name}**", expanded=True):
                                st.write(definition)
                else:
                    st.warning("⚠️ No Flashcards found in the generated response.")