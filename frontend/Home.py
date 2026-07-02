import re

import streamlit as st
from api import submit_lead


st.set_page_config(
    page_title="AI Lead Intake",
    page_icon=":clipboard:",
    layout="centered",
)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return len(digits) >= 10 and bool(re.match(r"^[0-9+\-\s()]+$", phone.strip()))


st.title("AI-Powered Lead Intake")
st.write(
    "Share your project requirements and our CRM will capture the lead, "
    "run AI qualification in the background, and trigger an acknowledgement email."
)

col1, col2, col3 = st.columns(3)
col1.info("Lead captured in CRM")
col2.info("AI score and reasoning")
col3.info("Automated email workflow")

st.divider()

with st.form("lead_form", clear_on_submit=True):
    st.subheader("Project Inquiry")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="Aarav Sharma")
        email = st.text_input("Email *", placeholder="aarav@example.com")
        phone = st.text_input("Phone Number *", placeholder="+91 98765 43210")
        company = st.text_input("Company Name", placeholder="Acme Technologies")

    with col2:
        industry = st.selectbox(
            "Industry",
            [
                "E-commerce",
                "SaaS",
                "Healthcare",
                "Education",
                "Finance",
                "Real Estate",
                "Manufacturing",
                "Other",
            ],
        )
        company_size = st.selectbox(
            "Company Size",
            ["1-10", "11-50", "51-200", "201-500", "500+"],
        )
        budget = st.number_input("Estimated Budget (INR)", min_value=0, step=10000)

    description = st.text_area(
        "Project Description *",
        height=140,
        placeholder="Tell us what you want to build, your goals, and expected timeline.",
    )

    submitted = st.form_submit_button("Submit Inquiry", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip() or not phone.strip() or not description.strip():
            st.error("Please fill in all required fields marked with *.")
        elif not is_valid_email(email):
            st.error("Please enter a valid email address.")
        elif not is_valid_phone(phone):
            st.error("Please enter a valid phone number with at least 10 digits.")
        else:
            lead_payload = {
                "name": name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "company": company.strip(),
                "industry": industry,
                "company_size": company_size,
                "budget": float(budget),
                "description": description.strip(),
            }

            with st.spinner("Saving lead and starting AI qualification..."):
                success, result = submit_lead(lead_payload)

            if success:
                lead_id = result.get("id") if isinstance(result, dict) else None
                st.success(
                    "Lead saved successfully. AI qualification and email automation are "
                    "running in the background."
                )
                if lead_id:
                    st.info(f"Lead ID: {lead_id}. Open the Dashboard in a few seconds to review the AI result.")
                else:
                    st.info("Open the Dashboard in a few seconds to review the AI result.")
            else:
                st.error(f"Something went wrong while submitting your inquiry: {result}")

st.divider()
st.caption("Sales team: open the Dashboard page from the sidebar to review and manage leads.")
