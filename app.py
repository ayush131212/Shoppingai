import os
import google.generativeai as genai
from flask import Flask, render_template, request
from dotenv import load_dotenv

# --- Initialization ---
load_dotenv()

app = Flask(__name__)

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

def generate_product_list_with_gemini(query):
    """
    Asks Gemini to act as a product search engine and generate HTML.
    """
    if not model:
        return "<p>Error: The AI model is not configured. Please check your API key.</p>"

    # This prompt is the core of the entire application.
    # It asks Gemini to guess sellers, products, prices, and generate search links.
    prompt = f"""
    You are an expert product search engine. A user is searching for "{query}".
    Your task is to generate a list of 5 plausible product listings from major online retailers
    who you estimate would sell this product a lot.

    Follow these rules STRICTLY:
    1.  Based on your knowledge, identify 5 major online retailers (like Amazon, Best Buy, Walmart, Target, B&H Photo, etc.) that likely sell "{query}".
    2.  For each retailer, invent a realistic product title and price.
    3.  Generate a valid SEARCH URL for the product on the retailer's website. For example, for Amazon, the URL should be like `https://www.amazon.com/s?k=sony+wh-1000xm5`. For Best Buy, `https://www.bestbuy.com/site/searchpage.jsp?st=sony+wh-1000xm5`.
    4.  Format the entire output as a block of HTML.
    5.  For each product, create a `div` with class "product-card".
    6.  Inside the card, put the product title in an `h3` tag.
    7.  Below the title, add a `p` tag with the seller's name and the estimated price. (e.g., "Seller: Amazon, Estimated Price: $349.99").
    8.  Finally, create a link (`<a>` tag) with class "product-link" that says "Search on Seller's Site". The href for this link MUST be the search URL you generated. It must open in a new tab.
    9.  Do NOT include any other text, explanation, or code block formatting like ```html. Only output the raw HTML content starting from the first `div`.

    Example for "running shoes":
    <div class="product-card"><h3>Nike Air Zoom Pegasus</h3><p>Seller: Nike, Estimated Price: $129.99</p><a href="https://www.nike.com/w?q=running shoes" class="product-link" target="_blank">Search on Seller's Site</a></div>
    <div class="product-card"><h3>Adidas Ultraboost</h3><p>Seller: Amazon, Estimated Price: $179.99</p><a href="https://www.amazon.com/s?k=running+shoes" class="product-link" target="_blank">Search on Seller's Site</a></div>
    ... and so on for 5 total products.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return f"<p>Sorry, there was an error with the AI assistant: {e}</p>"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_query = request.form.get('product_query')
        if not product_query:
            return render_template('index.html', results="<p>Please enter a product to search.</p>")
        
        # Call our single function to get the HTML from Gemini
        formatted_results = generate_product_list_with_gemini(product_query)
        
        return render_template('index.html', results=formatted_results)

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
