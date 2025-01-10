document.getElementById("review-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    const url = document.getElementById("product-url").value;
    const apiUrl = "https://api-for-product-review-1.onrender.com/api/reviews?page=" + encodeURIComponent(url);

    document.getElementById("reviews-container").innerHTML = "Loading reviews...";
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.reviews) {
            const reviewsHTML = data.reviews.map(review => `
                <div class="review">
                    <h3>${review.title} (${review.rating} stars)</h3>
                    <p>${review.body}</p>
                    <small>By: ${review.reviewer}</small>
                </div>
            `).join("");
            document.getElementById("reviews-container").innerHTML = reviewsHTML;
        } else {
            document.getElementById("reviews-container").innerHTML = "No reviews found.";
        }
    } catch (error) {
        document.getElementById("reviews-container").innerHTML = "Error fetching reviews.";
    }
});
