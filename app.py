import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Product Guesser",
    page_icon="🔮",
    layout="centered"
)

# --- API Configuration ---
# Load secrets for local development from .env file
load_dotenv()

# Use Streamlit's secrets management for deployment
try:
    # For Streamlit Community Cloud
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    # For local development
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
else:
    st.error("Gemini API key not found. Please set it in your secrets.")
    st.stop() # Stop the app if the key is not available

# --- The Core Gemini Function ---

def generate_product_list_with_gemini(query):
    """Asks Gemini to act as a product search engine and generate HTML."""

    # This prompt is the core of the entire application.
    # It tells Gemini to guess sellers, products, prices, and generate search links.
    prompt = f"""
    You are an expert product search engine. A user is searching for "{query}".
    Your task is to generate a list of 5 plausible product listings from major online retailers
    who you estimate would sell this product a lot.

    Follow these rules STRICTLY:
    1.  Based on your knowledge, identify 5 major online retailers (like Amazon, Best Buy, Walmart, Target, etc.) that likely sell "{query}".
    2.  For each retailer, invent a realistic product title and an estimated price.
    3.  Generate a valid SEARCH URL for the product on the retailer's website. For example, for Amazon, the URL should be like `https://www.amazon.com/s?k=sony+wh-1000xm5`. For Best Buy, `https://www.bestbuy.com/site/searchpage.jsp?st=sony+wh-1000xm5`.
    4.  Format the entire output as a block of HTML. Use inline CSS for styling.
    5.  For each product, create a `div` with `style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 1rem; padding: 1rem;"`.
    6.  Inside the card, put the product title in an `<h3>` tag.
    7.  Below the title, add a `<p>` tag with the seller's name and the estimated price (e.g., "Seller: Amazon, Estimated Price: $349.99").
    8.  Create a link (`<a>` tag) that says "Search on Seller's Site". The href MUST be the search URL you generated. It must open in a new tab (`target="_blank"`). Style it like a button with `style="display: inline-block; padding: 8px 16px; background-color: #0b57d0; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;"`
    9.  Do NOT include any other text, explanation, or code block formatting like ```html. Only output the raw HTML content starting from the first `div`.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while contacting the AI model: {e}")
        return None

# --- Streamlit User Interface ---

st.title("🔮 AI Product Guesser")
st.markdown("Enter a product, and Gemini will guess 5 places that might sell it and generate search links.")

with st.form(key="search_form"):
    product_query = st.text_input("Product Name", placeholder="e.g., Nintendo Switch OLED")
    submit_button = st.form_submit_button(label="Ask Gemini")

if submit_button and product_query:
    with st.spinner("🧠 Gemini is thinking..."):
        # Call our single function to get the HTML from Gemini
        formatted_html = generate_product_list_with_gemini(product_query)
        
        if formatted_html:
            st.markdown("### Here's what Gemini found:")
            st.markdown(formatted_html, unsafe_allow_html=True)
        else:
            st.warning("The AI could not generate a response. Please try again.")
