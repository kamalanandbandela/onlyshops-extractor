import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="OnlyShops Extractor Pro", layout="wide")

st.title("📦 OnlyShops Vendor Extractor Pro")
st.write("Upload your saved Google search HTML file to extract vendor info (phone, email, Insta, website, etc.)")

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
        location = ""
        website = ""

        # Title or Name
        title_tag = result.find("h3")
        if title_tag:
            name = title_tag.text.strip()

        # URL
        cite_tag = result.find("cite")
        if cite_tag:
            website = cite_tag.text.strip()
            if "instagram.com" in website:
                instagram = website

        # Snippet text
        snippet = result.get_text(separator=" ").strip()
        phone_match = re.search(r"(?:(?:\+91[\-\s]?)?[789]\d{9})", snippet)
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", snippet)
        location_match = re.search(r"(Hyderabad|Secunderabad|Vijayawada|Guntur|Vizag|.*City)", snippet, re.IGNORECASE)

        if phone_match:
            phone = phone_match.group()
        if email_match:
            email = email_match.group()
        if location_match:
            location = location_match.group()

        shop_name = name if "boutique" in name.lower() or "store" in name.lower() else ""

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
        st.success("✅ Data Extracted Successfully!")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="onlyshops_vendors.csv",
            mime="text/csv",
        )
    else:
        st.warning("No vendor data found. Try uploading a different file.")
