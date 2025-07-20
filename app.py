import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="OnlyShops Global Vendor Extractor", layout="wide")

st.title("🌍 OnlyShops Global Vendor Extractor")
st.write("Upload a saved Google Search HTML file to extract vendor contact data from any country (India, USA, Canada, etc.)")

uploaded_file = st.file_uploader("Upload Google Search HTML File", type=["html", "htm"])

def extract_info_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    results = soup.find_all("div", class_="tF2Cxc")
    data = []

    for result in results:
        name = ""
        shop_name = ""
        phone = ""
        email = ""
        instagram = ""
        website = ""
        location = ""

        # Extract title/name
        title_tag = result.find("h3")
        if title_tag:
            name = title_tag.get_text().strip()

        # Extract website or Instagram
        cite_tag = result.find("cite")
        if cite_tag:
            url = cite_tag.get_text().strip()
            if "instagram.com" in url:
                instagram = url
            else:
                website = url

        # Extract text snippet for data mining
        snippet = result.get_text(separator=" ").strip()

        # Extract international phone numbers
        phone_match = re.search(r"(\+\d{1,2}\s?)?(\()?\d{3}(\))?[-\s.]?\d{3}[-\s.]?\d{4}", snippet)
        if phone_match:
            phone = phone_match.group()

        # Extract emails
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", snippet)
        if email_match:
            email = email_match.group()

        # Basic location matching for major cities (expandable)
        location_match = re.search(r"(New York|Los Angeles|Chicago|Toronto|Vancouver|London|Sydney|Melbourne|Hyderabad|Mumbai|Delhi|Bangalore)", snippet, re.IGNORECASE)
        if location_match:
            location = location_match.group().title()

        # Improved shop name logic with global keywords
        keywords = ["boutique", "fashion", "wear", "retail", "store", "outfitters", "clothing", "apparel", "threads", "design", "studio"]
        if any(kw in name.lower() for kw in keywords):
            shop_name = name

        data.append({
            "Name": name,
            "Shop Name": shop_name,
            "Phone": phone,
            "Email": email,
            "Instagram": instagram,
            "Website": website,
            "Location": location
        })

    return data

if uploaded_file:
    html_content = uploaded_file.read()
    extracted_data = extract_info_from_html(html_content)
    df = pd.DataFrame(extracted_data)

    if not df.empty:
        st.success("✅ Global Vendor Data Extracted!")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Global CSV",
            data=csv,
            file_name="onlyshops_global_vendors.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data found. Try a different file or check formatting.")
