import json
from flask import Flask, request
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

# Function to extract reviews from the page
def extract_reviews_from_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=10000)  # Set a timeout for loading the page
        except Exception as e:
            return json.dumps({"error": f"Failed to load page: {str(e)}"}), 500

        reviews = []

        try:
            # Wait for the reviews to load (adjust the selector if necessary)
            page.wait_for_selector(".review", timeout=5000)  # Adjust this to match the actual review container selector
        except Exception:
            return json.dumps({"error": "No reviews found or page did not load correctly."}), 404

        review_elements = page.query_selector_all(".review")  # Adjust this to match the actual review element selector

        if not review_elements:
            # Return the page content if reviews are not found for debugging
            return json.dumps({"error": "No reviews found for this product.", "page_content": page.content()}), 404

        for review_element in review_elements:
            # Extract review title (rating + title) and body
            title_element = review_element.query_selector(".review-title")  # Replace with correct class
            title_text = title_element.inner_text() if title_element else "No title available"
            
            # Split the title to get the rating and the review body
            rating = 0
            title_split = title_text.split('\n', 1)  # Split at the first newline
            if len(title_split) > 1:
                rating_text = title_split[0]  # "5.0 out of 5 stars"
                review_title = title_split[1]  # "Good product"
                
                # Extract numeric rating from the text (e.g., "5.0")
                rating = float(rating_text.split(' ')[0]) if rating_text.split(' ')[0].replace('.', '', 1).isdigit() else 0
            else:
                review_title = title_text

            # Extract the review body (if available)
            body_element = review_element.query_selector(".review-text")  # Replace with the actual class for the body
            body = body_element.inner_text() if body_element else "No review body available"
            body = body.strip().replace("\n", " ")

            # Extract reviewer name (if available)
            reviewer_element = review_element.query_selector(".reviewer-name")  # Replace with the correct class
            reviewer = reviewer_element.inner_text() if reviewer_element else "Anonymous"

            # Append the review to the list
            reviews.append({
                "title": review_title,
                "body": body,
                "rating": rating,
                "reviewer": reviewer
            })

        browser.close()
        return reviews


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    url = request.args.get('page')
    
    if not url:
        return json.dumps({"error": "Please provide a product URL."}), 400

    reviews = extract_reviews_from_page(url)
    
    if isinstance(reviews, tuple):  # Check if the response is an error message
        return reviews

    return json.dumps({
        "reviews_count": len(reviews),
        "reviews": reviews
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable, or default to 5000
    app.run(host='0.0.0.0', port=port)
