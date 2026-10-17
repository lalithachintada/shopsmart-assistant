
import streamlit as st
import pandas as pd
import time
import re

st.set_page_config(
    page_title="ShopSmart Assistant",
    page_icon="🛍️",
    layout="wide"
)

# Sample data only — not an official retailer catalogue
products = [
    {
        "id": "P101", "title": "Blue Cotton T-Shirt",
        "category": "Clothing", "color": "Blue",
        "material": "Cotton", "price": 799,
        "stock": "In stock", "rating": 4.3
    },
    {
        "id": "P102", "title": "Blue Running Shoes",
        "category": "Footwear", "color": "Blue",
        "material": "Mesh", "price": 1499,
        "stock": "In stock", "rating": 4.2
    },
    {
        "id": "P103", "title": "Blue Running Shoes Pro",
        "category": "Footwear", "color": "Blue",
        "material": "Mesh", "price": 2499,
        "stock": "Out of stock", "rating": 4.5
    },
    {
        "id": "P104", "title": "White Cotton T-Shirt",
        "category": "Clothing", "color": "White",
        "material": "Cotton", "price": 599,
        "stock": "In stock", "rating": 4.1
    }
]

df = pd.DataFrame(products)

# Custom styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .subtitle {
        color: #777;
        font-size: 1.05rem;
    }
    .product-title {
        font-size: 1.15rem;
        font-weight: 700;
    }
    .price {
        font-size: 1.8rem;
        font-weight: 800;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    '<div class="main-title">🛍️ ShopSmart Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Find products. Compare options. '
    'Get honest answers.</div>',
    unsafe_allow_html=True
)

st.write("")
st.info(
    "Demo mode: All products below are sample data. "
    "This app is not connected to a real retailer catalogue."
)

# Product catalogue
st.subheader("🛒 Featured Products")
st.caption("Explore our four demo products.")

cols = st.columns(2)

for i, product in enumerate(products):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(
                f'<div class="product-title">{product["title"]}</div>',
                unsafe_allow_html=True
            )
            st.caption(f'Product ID: {product["id"]}')
            st.markdown(
                f'<div class="price">₹{product["price"]:,}</div>',
                unsafe_allow_html=True
            )

            if product["stock"] == "In stock":
                st.success("● In stock")
            else:
                st.error("● Out of stock")

            st.write(f'⭐ {product["rating"]} / 5')
            st.caption(
                f'{product["color"]} • {product["material"]} • '
                f'{product["category"]}'
            )

st.divider()

# Chat section
st.subheader("💬 Ask ShopSmart")
st.caption(
    'Try: "Find blue shoes", "Show shoes under 2000", '
    'or "What is the return policy?"'
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def answer_question(question):
    q = question.lower().strip()

    # Never invent unsupported product or policy information
    if "iphone" in q:
        return (
            "I couldn't find an iPhone in the available demo catalogue. "
            "I can't confirm whether the retailer sells it."
        )

    if any(word in q for word in [
        "return policy", "refund policy", "warranty",
        "shipping policy", "return rules", "refund rules"
    ]):
        return (
            "I don't have the official policy document, so I can't "
            "confirm the retailer's return, warranty, or shipping rules."
        )

    matches = df.copy()

    # Filter by explicitly requested colour
    colours = ["blue", "white", "black", "red", "green", "yellow"]
    requested_colour = next((c for c in colours if c in q), None)

    if requested_colour:
        matches = matches[
            matches["color"].str.lower() == requested_colour
        ]

    # Filter by explicitly requested material
    materials = ["cotton", "mesh", "leather", "wool", "denim"]
    requested_material = next((m for m in materials if m in q), None)

    if requested_material:
        matches = matches[
            matches["material"].str.lower() == requested_material
        ]

    # Filter by product type
    if any(word in q for word in ["shoe", "shoes", "footwear", "sneaker"]):
        matches = matches[matches["category"] == "Footwear"]

    if any(word in q for word in ["shirt", "t-shirt", "tshirt", "tee"]):
        matches = matches[
            matches["title"].str.lower().str.contains("t-shirt")
        ]

    # Filter by maximum budget
    if any(word in q for word in ["under", "below", "budget", "less than"]):
        amounts = re.findall(r"\d[\d,]*", q)

        if amounts:
            budget = int(amounts[-1].replace(",", ""))
            matches = matches[matches["price"] <= budget]

    if matches.empty:
        return (
            "I couldn't find a matching product in the available "
            "demo catalogue. Try a different colour, product type, "
            "or budget. I won't invent a product."
        )

    # Show useful comparison details instead of guessing
    if len(matches) > 1:
        lines = [
            "I found multiple matching products. Here are the options:"
        ]

        for _, p in matches.iterrows():
            lines.append(
                f'- **{p["title"]}** (ID: {p["id"]})\n'
                f'  - Price: ₹{p["price"]:,}\n'
                f'  - Availability: {p["stock"]}\n'
                f'  - Rating: {p["rating"]} / 5'
            )

        lines.append(
            "\nWhich product would you like to know more about?"
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


# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask me about products or prices...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    start = time.perf_counter()
    response = answer_question(question)
    latency = time.perf_counter() - start

    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"Response time: {latency:.4f} seconds")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

