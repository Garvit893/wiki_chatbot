import streamlit as st
import google.generativeai as genai
import requests

# --- Get API key from Streamlit secrets.toml (section: [gemini]) ---
api_key = st.secrets["gemini"]["api_key"]
if not api_key:
    st.error("API NOT FOUND")
    st.stop()
genai.configure(api_key=api_key)
# ---------------------------------------------------------------

model = genai.GenerativeModel("models/gemini-2.5-flash")  # Use a valid Gemini model

def fetch_wikipedia_content(url):
    """Fetch raw text from a Wikipedia article using the Wikipedia API."""
    try:
        if not url.startswith("https://en.wikipedia.org/wiki/"):
            st.error("Please enter a valid English Wikipedia article URL.")
            return ""
        title = url.split("/wiki/")[-1]
        endpoint = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "titles": title,
            "format": "json"
        }
        headers = {"User-Agent": "Wikipedia-Chatbot/1.0"}
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        pages = response.json()["query"]["pages"]
        text = next(iter(pages.values())).get("extract", "")
        return text
    except Exception as e:
        st.error(f"Could not fetch article: {e}")
        return ""

def gemini_qa(context, question):
    prompt = f"""You are an intelligent Wikipedia assistant. Answer only using the context below. If the answer is not present, reply "I don't know this question."
Context:
{context}

User question: {question}
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def main():
    st.title("Wikipedia URL Q&A Chatbot 🤖")
    st.markdown("Paste a Wikipedia URL below. The bot will fetch the article and answer your questions!")
    url = st.text_input("Wikipedia URL (e.g., https://en.wikipedia.org/wiki/Adrian_Carton_de_Wiart):")
    article_text = ""
    if url:
        with st.spinner("Fetching Wikipedia article..."):
            article_text = fetch_wikipedia_content(url)
        if article_text:
            st.success("Article loaded! (You may edit the context below)")

    context = st.text_area("Wikipedia article text (edit if needed):", value=article_text, height=300)
    question = st.text_input("Your question:")
    if st.button("Enter"):
        if not context.strip():
            st.warning("Paste or load Wikipedia text first!")
        elif not question.strip():
            st.warning("Enter your question.")
        else:
            with st.spinner("Getting answers..."):
                answer = gemini_qa(context[:15000], question)  # Truncate to safe context limit
                st.markdown(f"**Answer:**\n\n{answer}")

if __name__ == "__main__":
    main()
