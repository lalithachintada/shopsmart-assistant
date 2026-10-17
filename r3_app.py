from difflib import get_close_matches
import streamlit as st
import pandas as pd
import time
import re

st.set_page_config(
    page_title="R3 Shopping Assistant",
    page_icon="🛍️"
)

# SAMPLE DATA ONLY — replace with official catalogue later
products = [
    {
        "id": "P101",
        "title": "Blue Cotton T-Shirt",
        "category": "Clothing",
        "color": "Blue",
        "material": "Cotton",
        "price": 799,
        "stock": "In stock",
        "rating": 4.3
    },
    {
        "id": "P102",
        "title": "Blue Running Shoes",
        "category": "Footwear",
        "color": "Blue",
        "material": "Mesh",
        "price": 1499,
        "stock": "In stock",
        "rating": 4.2
    },
    {
        "id": "P103",
        "title": "Blue Running Shoes Pro",
        "category": "Footwear",
        "color": "Blue",
        "material": "Mesh",
        "price": 2499,
        "stock": "Out of stock",
        "rating": 4.5
    },
    {
        "id": "P104",
        "title": "White Cotton T-Shirt",
        "category": "Clothing",
        "color": "White",
        "material": "Cotton",
        "price": 599,
        "stock": "In stock",
        "rating": 4.1
    }
]

df = pd.DataFrame(products)


st.title("🛍️ ShopSmart Assistant")
st.caption("Your shopping helper — accurate answers, no guessing.")

st.markdown("---")
st.subheader("🛒 Featured Products")

cols = st.columns(2)

for i, product in enumerate(products):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {product['title']}")
            st.caption(f"Product ID: {product['id']}")
            st.markdown(f"## ₹{product['price']}")
            st.write(f"📦 {product['stock']}")
            st.write(f"⭐ {product['rating']} / 5")


st.warning(
    "Demo mode: These are sample products, not the official catalogue."
)

if "messages" not in st.session_state:
    st.session_state.messages = []



def answer_question(question):
    q = question.lower().strip()

    if not q:
        return "Please enter a product name or question."

    if q in ["hi", "hello", "hey", "hi bro", "hello bro"]:
        return "Hello! 👋 I'm ShopSmart Assistant. What product are you looking for?"

    if any(word in q for word in [
        "return policy", "refund policy", "warranty",
        "shipping policy", "return rules", "refund rules"
    ]):
        return (
            "I don't have the official policy document, so I can't "
            "confirm the retailer's return, warranty, or shipping rules."
        )

    # Correct common spelling mistakes in product-related words
    corrections = {
        "shirst": "shirt",
        "shrit": "shirt",
        "tshrit": "tshirt",
        "cotn": "cotton",
        "cotten": "cotton",
        "blu": "blue",
        "shooes": "shoes",
        "shose": "shoes",
        "sneekers": "sneakers",
        "bangles": "bangles",
    }

    words = re.findall(r"[a-z]+|\d[\d,]*", q)
    fixed_words = [corrections.get(word, word) for word in words]
    q = " ".join(fixed_words)

    # Reject unsupported product types
    if re.search(r"\b(iphone|i-phone|bangle|bangles)\b", q):
        return (
            "I couldn't find that product in our demo catalogue. "
            "I can't confirm whether a real retailer sells it."
        )

    shoe_words = ["shoe", "shoes", "footwear", "sneaker", "sneakers"]
    shirt_words = ["shirt", "shirts", "t-shirt", "tshirt", "tee", "tees"]
    colours = ["blue", "white", "black", "red", "green", "yellow"]
    materials = ["cotton", "mesh", "leather", "wool", "denim"]

    wants_shoes = any(word in q for word in shoe_words)
    wants_shirt = any(word in q for word in shirt_words)
    requested_colour = next(
        (c for c in colours if re.search(r"\b" + c + r"\b", q)), None
    )
    requested_material = next(
        (m for m in materials if re.search(r"\b" + m + r"\b", q)), None
    )

    has_budget_word = any(word in q for word in [
        "under", "below", "budget", "less than"
    ])
    amounts = re.findall(r"\d[\d,]*", q)
    has_budget = has_budget_word and bool(amounts)

    # Only allow searches with a supported product type
    if not (wants_shoes or wants_shirt):
        return (
            "I couldn't find a matching product in our demo catalogue. "
            "Try blue shoes, cotton T-shirts, or shoes under 2000."
        )

    matches = df.copy()

    if requested_colour:
        matches = matches[
            matches["color"].str.lower() == requested_colour
        ]

    if requested_material:
        matches = matches[
            matches["material"].str.lower() == requested_material
        ]

    if wants_shoes:
        matches = matches[matches["category"] == "Footwear"]

    if wants_shirt:
        matches = matches[
            matches["title"].str.lower().str.contains(
                "t-shirt", regex=False
            )
        ]

    if has_budget:
        budget = int(amounts[-1].replace(",", ""))
        matches = matches[matches["price"] <= budget]

    if matches.empty:
        return (
            "I couldn't find a matching product in our demo catalogue. "
            "Try another colour, material, product type, or budget."
        )

    if len(matches) > 1:
        lines = ["Here are the matching products in our demo catalogue:"]
        for _, p in matches.iterrows():
            lines.append(
                f'- **{p["title"]}** (ID: {p["id"]})\n'
                f'  - Price: ₹{p["price"]:,}\n'
                f'  - Availability: {p["stock"]}\n'
                f'  - Rating: {p["rating"]} / 5'
            )
        return "\n\n".join(lines)

    p = matches.iloc[0]
    return (
        f'**{p["title"]}**\n\n'
        f'- **Product ID:** {p["id"]}\n'
        f'- **Price:** ₹{p["price"]:,}\n'
        f'- **Availability:** {p["stock"]}\n'
        f'- **Rating:** ⭐ {p["rating"]} / 5'
    )

st.markdown("---")
st.subheader("💬 Chat with ShopSmart")

# Display previous conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input bar
if prompt := st.chat_input("Ask about products, prices, stock..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    response = answer_question(prompt)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)



     

   
