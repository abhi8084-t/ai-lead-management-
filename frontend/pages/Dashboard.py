import os
import sys
from datetime import date

import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import get_all_leads, get_dashboard_stats, get_lead_by_id, update_lead


st.set_page_config(page_title="CRM Dashboard", page_icon=":bar_chart:", layout="wide")

st.markdown(
    """
    <style>
    .crm-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 14px 16px;
        background: #ffffff;
    }
    .crm-label {
        color: #6b7280;
        font-size: 0.82rem;
        margin-bottom: 4px;
    }
    .crm-value {
        color: #111827;
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .badge {
        border-radius: 999px;
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 4px 10px;
    }
    .badge-new { background: #fef3c7; color: #92400e; }
    .badge-qualified { background: #dcfce7; color: #166534; }
    .badge-lost { background: #fee2e2; color: #991b1b; }
    .badge-hot { background: #fee2e2; color: #991b1b; }
    .badge-warm { background: #fef3c7; color: #92400e; }
    .badge-cold { background: #dbeafe; color: #1e40af; }
    .muted { color: #6b7280; }
    .mini-panel {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 14px 16px;
        background: #ffffff;
        min-height: 190px;
    }
    .mini-title {
        color: #111827;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .bar-row {
        display: grid;
        grid-template-columns: 92px 1fr 32px;
        align-items: center;
        gap: 10px;
        margin: 10px 0;
    }
    .bar-label {
        color: #374151;
        font-size: 0.86rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .bar-track {
        background: #f3f4f6;
        border-radius: 999px;
        height: 9px;
        overflow: hidden;
    }
    .bar-fill {
        background: #2563eb;
        border-radius: 999px;
        height: 100%;
    }
    .bar-count {
        color: #111827;
        font-size: 0.86rem;
        font-weight: 700;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def parse_date(value):
    if not value:
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return date.today()


def badge(value, kind):
    label = value or "-"
    css_value = str(label).lower().replace(" ", "-")
    return f'<span class="badge badge-{css_value}">{label}</span>'


def card(label, value):
    st.markdown(
        f"""
        <div class="crm-card">
            <div class="crm-label">{label}</div>
            <div class="crm-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mini_distribution(title, counts):
    max_count = max(counts.values()) if counts else 0
    rows = []

    for label, count in counts.items():
        width = 0 if max_count == 0 else max(8, int((count / max_count) * 100))
        rows.append(
            f'<div class="bar-row">'
            f'<div class="bar-label" title="{label}">{label}</div>'
            f'<div class="bar-track">'
            f'<div class="bar-fill" style="width: {width}%"></div>'
            f'</div>'
            f'<div class="bar-count">{count}</div>'
            f'</div>'
        )

    body = "".join(rows) if rows else '<div class="muted">No data available</div>'
    st.markdown(
        f'<div class="mini-panel"><div class="mini-title">{title}</div>{body}</div>',
        unsafe_allow_html=True,
    )


def score_progress(score):
    score = int(score or 0)
    st.progress(score / 100)


def select_lead(lead_id):
    st.session_state["selected_lead_id"] = int(lead_id)


st.title("CRM Dashboard")
st.caption("Review captured leads, inspect AI qualification, and update CRM fields from one screen.")

stats = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    card("Total Leads", stats["total_leads"])
with col2:
    card("New Leads", stats["new_leads"])
with col3:
    card("Qualified Leads", stats["qualified_leads"])
with col4:
    card("Lost Leads", stats["lost_leads"])

st.divider()

leads = get_all_leads()

if not leads:
    st.info("No leads yet. Submit a lead from the Home page to start reviewing the pipeline.")
else:
    df = pd.DataFrame(leads)

    today_count = 0
    if "created_at" in df.columns:
        created_dates = pd.to_datetime(df["created_at"], errors="coerce").dt.date
        today_count = int((created_dates == date.today()).sum())

    pending_follow_up = int(
        df["follow_up_date"].notna().sum()
        if "follow_up_date" in df.columns
        else 0
    )

    scol1, scol2, scol3 = st.columns(3)
    scol1.info(f"Today's leads: {today_count}")
    scol2.info(f"Need follow-up: {pending_follow_up}")
    scol3.info(f"Awaiting AI: {int(df['score'].isna().sum()) if 'score' in df.columns else 0}")

    with st.expander("Search and filters", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            status_options = sorted(df["status"].dropna().unique().tolist())
            status_filter = st.multiselect("Status", options=status_options, default=status_options)
        with fcol2:
            temp_options = sorted(df["temperature"].dropna().unique().tolist())
            temp_filter = st.multiselect("Temperature", options=temp_options, default=temp_options)
        with fcol3:
            industry_options = sorted(df["industry"].dropna().unique().tolist())
            industry_filter = st.multiselect("Industry", options=industry_options, default=industry_options)
        with fcol4:
            search = st.text_input("Search", placeholder="Name, email, company, industry")

    filtered_df = df[df["status"].isin(status_filter)] if status_filter else df.iloc[0:0]

    if temp_filter:
        filtered_df = filtered_df[
            filtered_df["temperature"].isin(temp_filter) | filtered_df["temperature"].isna()
        ]

    if industry_filter:
        filtered_df = filtered_df[filtered_df["industry"].isin(industry_filter)]

    if search:
        query = search.strip()
        mask = (
            filtered_df["name"].str.contains(query, case=False, na=False)
            | filtered_df["email"].str.contains(query, case=False, na=False)
            | filtered_df["company"].str.contains(query, case=False, na=False)
            | filtered_df["industry"].str.contains(query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    ccol1, ccol2 = st.columns([1, 1])
    with ccol1:
        status_counts = df["status"].fillna("Unknown").value_counts().to_dict()
        mini_distribution("Lead Distribution", status_counts)
    with ccol2:
        temp_counts = df["temperature"].fillna("Pending").value_counts().to_dict()
        mini_distribution("AI Temperature", temp_counts)

    export_col, spacer_col = st.columns([1, 2])
    with export_col:
        st.download_button(
            "Export Leads CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="leads.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    st.subheader("Lead Pipeline")

    if filtered_df.empty:
        st.warning("No leads match the current filters.")
    else:
        header = st.columns([0.6, 1.5, 1.5, 1, 1.1, 1])
        header[0].markdown("**ID**")
        header[1].markdown("**Name**")
        header[2].markdown("**Company**")
        header[3].markdown("**Score**")
        header[4].markdown("**Status**")
        header[5].markdown("**Action**")

        for _, row in filtered_df.head(25).iterrows():
            row_cols = st.columns([0.6, 1.5, 1.5, 1, 1.1, 1])
            row_cols[0].write(int(row["id"]))
            row_cols[1].write(row["name"])
            row_cols[2].write(row.get("company") or "-")
            row_cols[3].write("-" if pd.isna(row.get("score")) else f"{int(row['score'])}/100")
            row_cols[4].markdown(badge(row.get("status"), "status"), unsafe_allow_html=True)
            if row_cols[5].button("View", key=f"view_{int(row['id'])}", use_container_width=True):
                select_lead(row["id"])
                st.rerun()

        if len(filtered_df) > 25:
            st.caption("Showing first 25 filtered leads. Use search or filters to narrow the list.")

        if "selected_lead_id" not in st.session_state:
            st.session_state["selected_lead_id"] = int(filtered_df.iloc[0]["id"])

        selected_id = st.session_state["selected_lead_id"]
        if selected_id not in filtered_df["id"].tolist():
            selected_id = int(filtered_df.iloc[0]["id"])
            st.session_state["selected_lead_id"] = selected_id

        st.divider()
        st.subheader("Lead Review")

        lead = get_lead_by_id(selected_id)

        if not lead:
            st.error("Lead not found. Refresh the page and try again.")
        else:
            if st.button("Open Full Details Page", use_container_width=True):
                st.session_state["selected_lead_id"] = selected_id
                st.switch_page("pages/Lead_Details.py")

            left, right = st.columns([1, 1])

            with left:
                st.markdown("**Contact**")
                st.write(f"Name: {lead['name']}")
                st.write(f"Email: {lead['email']}")
                st.write(f"Phone: {lead['phone']}")
                st.write(f"Company: {lead.get('company') or '-'}")
                st.write(f"Industry: {lead.get('industry') or '-'}")
                st.write(f"Company Size: {lead.get('company_size') or '-'}")
                st.write(f"Budget: INR {lead.get('budget') or 0:,.0f}")
                email_status = "Delivered" if lead.get("email_sent") == "Yes" else "Not sent"
                st.write(f"Email: {email_status}")
                st.markdown(badge(lead.get("status"), "status"), unsafe_allow_html=True)

            with right:
                st.markdown("**AI Qualification**")
                if lead.get("score") is None:
                    st.warning("AI qualification is still running. Refresh in a few seconds.")
                else:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Score", f"{lead['score']}/100")
                    m2.markdown(badge(lead.get("temperature"), "temperature"), unsafe_allow_html=True)
                    m3.metric("Confidence", f"{lead.get('confidence') or 0}%")
                    score_progress(lead["score"])
                    st.info(lead.get("reasoning") or "No reasoning available.")
                    st.success(f"Recommended action: {lead.get('next_action') or '-'}")

            st.markdown("**Project Description**")
            st.write(lead["description"])

            st.markdown("**Timeline**")
            t1, t2, t3, t4 = st.columns(4)
            t1.write("Lead submitted")
            t2.write("AI qualification" if lead.get("score") is not None else "AI pending")
            t3.write("Email delivered" if lead.get("email_sent") == "Yes" else "Email pending")
            t4.write("CRM review")

            st.markdown("**CRM Update**")
            with st.form("crm_update_form"):
                status_values = ["New", "Qualified", "Lost"]
                current_status = lead.get("status") if lead.get("status") in status_values else "New"
                status = st.selectbox(
                    "Status",
                    status_values,
                    index=status_values.index(current_status),
                )
                owner = st.text_input("Owner", value=lead.get("owner") or "")
                follow_up_date = st.date_input(
                    "Follow-up Date",
                    value=parse_date(lead.get("follow_up_date")),
                )
                notes = st.text_area("Notes", value=lead.get("notes") or "", height=120)

                submitted = st.form_submit_button("Save CRM Changes", use_container_width=True)

            if submitted:
                payload = {
                    "status": status,
                    "owner": owner.strip(),
                    "follow_up_date": str(follow_up_date),
                    "notes": notes.strip(),
                }
                success, result = update_lead(selected_id, payload)
                if success:
                    st.success("Lead updated successfully.")
                    st.rerun()
                else:
                    st.error(f"Failed to update lead: {result}")
