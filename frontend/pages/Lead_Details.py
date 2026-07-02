import os
import sys
from datetime import date

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import get_all_leads, get_lead_by_id, update_lead


st.set_page_config(page_title="Lead Details", page_icon=":mag:", layout="wide")


def parse_date(value):
    if not value:
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return date.today()


def status_label(status):
    labels = {
        "New": "New lead",
        "Qualified": "Qualified lead",
        "Lost": "Lost lead",
    }
    return labels.get(status, status or "-")


st.title("Lead Details")
st.caption("Open a lead, review AI qualification, and update sales follow-up fields.")

leads = get_all_leads()

if not leads:
    st.info("No leads are available yet. Submit a lead from the Home page first.")
else:
    lead_ids = [lead["id"] for lead in leads]
    default_id = st.session_state.get("selected_lead_id", lead_ids[0])
    default_index = lead_ids.index(default_id) if default_id in lead_ids else 0

    selected_id = st.selectbox(
        "Select Lead",
        options=lead_ids,
        index=default_index,
        format_func=lambda lead_id: next(
            f"#{lead['id']} - {lead['name']} ({lead.get('company') or 'No company'})"
            for lead in leads
            if lead["id"] == lead_id
        ),
    )
    st.session_state["selected_lead_id"] = selected_id

    lead = get_lead_by_id(selected_id)

    if not lead:
        st.error("Lead not found. Refresh the page and try again.")
    else:
        top1, top2, top3, top4 = st.columns(4)
        top1.metric("Score", "-" if lead.get("score") is None else f"{lead['score']}/100")
        top2.metric("Temperature", lead.get("temperature") or "Pending")
        top3.metric("Status", status_label(lead.get("status")))
        top4.metric("Email", "Delivered" if lead.get("email_sent") == "Yes" else "Pending")

        if lead.get("score") is not None:
            st.progress(int(lead["score"]) / 100)

        st.divider()

        contact, ai = st.columns([1, 1])

        with contact:
            st.subheader("Contact")
            st.write(f"Name: {lead['name']}")
            st.write(f"Email: {lead['email']}")
            st.write(f"Phone: {lead['phone']}")
            st.write(f"Company: {lead.get('company') or '-'}")
            st.write(f"Industry: {lead.get('industry') or '-'}")
            st.write(f"Company Size: {lead.get('company_size') or '-'}")
            st.write(f"Budget: INR {lead.get('budget') or 0:,.0f}")

        with ai:
            st.subheader("AI Qualification")
            if lead.get("score") is None:
                st.warning("AI is still analyzing this lead. Refresh in a few seconds.")
            else:
                st.write(f"Confidence: {lead.get('confidence') or 0}%")
                st.info(lead.get("reasoning") or "No reasoning available.")
                st.success(f"Recommended action: {lead.get('next_action') or '-'}")

        st.subheader("Project Description")
        st.write(lead["description"])

        st.subheader("Timeline")
        t1, t2, t3, t4 = st.columns(4)
        t1.write("Lead submitted")
        t2.write("AI completed" if lead.get("score") is not None else "AI pending")
        t3.write("Email delivered" if lead.get("email_sent") == "Yes" else "Email pending")
        t4.write("CRM follow-up")

        st.divider()
        st.subheader("Manage Lead")

        with st.form("lead_detail_update_form"):
            status_options = ["New", "Qualified", "Lost"]
            current_status = lead.get("status") if lead.get("status") in status_options else "New"

            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status),
            )
            new_owner = st.text_input("Owner", value=lead.get("owner") or "")
            new_follow_up = st.date_input(
                "Follow-up Date",
                value=parse_date(lead.get("follow_up_date")),
            )
            new_notes = st.text_area("Notes", value=lead.get("notes") or "", height=130)

            submitted = st.form_submit_button("Save Changes", use_container_width=True)

        if submitted:
            update_payload = {
                "status": new_status,
                "notes": new_notes.strip(),
                "owner": new_owner.strip(),
                "follow_up_date": str(new_follow_up),
            }
            success, result = update_lead(selected_id, update_payload)
            if success:
                st.success("Lead updated successfully.")
                st.rerun()
            else:
                st.error(f"Failed to update lead: {result}")
