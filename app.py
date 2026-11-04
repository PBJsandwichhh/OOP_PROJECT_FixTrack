import streamlit as st
import pandas as pd

from repair_tracker import RepairJobTracker, DATA_FILE
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="FixTrack",
    page_icon="🔧",
    layout="wide"
)

# STYLE
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #1F4E78;
    margin-bottom: 0;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-top: 0;
}

[data-testid="stAppViewContainer"] {
    background-color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #1E293B;
}

[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# TRACKER
if "tracker" not in st.session_state:
    st.session_state.tracker = RepairJobTracker()

tracker = st.session_state.tracker

STATUSES = [
    "Received",
    "Diagnosing",
    "Repairing",
    "Ready for Pickup",
    "Completed"
]

PROBLEM_TYPES = [
    "Hardware",
    "Software",
    "Screen / Display",
    "Battery / Power",
    "Other"
]

# HEADER
st.markdown(
    '<p class="main-title">FIXTRACK</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Repair Job Tracker</p>',
    unsafe_allow_html=True
)

st.divider()

# SIDEBAR
with st.sidebar:
    st.markdown(
        "<h2 style='color:#ffffff; "
        "font-size:35px; "
        "font-weight:bold;'>FIXTRACK MENU</h2>",
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Repair Job",
            "View Repair Jobs",
            "Search Jobs",
            "Update Job"
        ],
        label_visibility="collapsed"
    )

# DASHBOARD
if page == "Dashboard":
    st.header("Dashboard")
    total = len(tracker.jobs)
    active = sum(
        job.status != "Completed"
        for job in tracker.jobs
    )

    ready = sum(
        job.status == "Ready for Pickup"
        for job in tracker.jobs
    )

    completed = sum(
        job.status == "Completed"
        for job in tracker.jobs
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Jobs",
        total
    )

    c2.metric(
        "Active Repairs",
        active
    )

    c3.metric(
        "Ready for Pickup",
        ready
    )

    c4.metric(
        "Completed",
        completed
    )

    # DELAY RISK MONITOR
    st.subheader("Delay Risk Monitor")

    active_jobs = [
        job for job in tracker.jobs
        if job.status != "Completed"
    ]

    if active_jobs:
        high = 0
        medium = 0
        low = 0

        risk_results = []

        for job in active_jobs:
            risk = tracker.calculate_delay_risk(job)
            risk_results.append(
                (job, risk)
            )

            if risk["level"] == "High":
                high += 1

            elif risk["level"] == "Medium":
                medium += 1

            else:
                low += 1

        r1, r2, r3 = st.columns(3)

        r1.metric(
            "🔴 High Risk",
            high
        )

        r2.metric(
            "🟡 Medium Risk",
            medium
        )

        r3.metric(
            "🟢 Low Risk",
            low
        )

        for job, risk in risk_results:
            if risk["level"] == "High":
                with st.expander(
                    f"🔴 {job.job_id} — {job.customer_name}"
                ):

                    st.write(
                        f"**Item:** {job.item}"
                    )

                    st.write(
                        f"**Risk Score:** "
                        f"{risk['score']}/100"
                    )

                    if risk["reasons"]:
                        st.write("**Risk Factors:**")
                        for reason in risk["reasons"]:
                            st.write(
                                f"- {reason}"
                            )

    else:
        st.success(
            "No active repairs currently at risk."
        )

    # RECENT JOBS
    st.subheader("Recent Repair Jobs")

    if tracker.jobs:
        recent = tracker.jobs[-5:][::-1]
        df = pd.DataFrame([
            {
                "Job ID": job.job_id,
                "Customer": job.customer_name,
                "Item": job.item,
                "Status": job.status,
                "Cost": f"₱{job.cost:,.2f}"
            }

            for job in recent
        ])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No repair jobs have been added yet."
        )

# ADD REPAIR JOB
elif page == "Add Repair Job":
    st.header("Add Repair Job")
    with st.form("add_job"):
        customer = st.text_input(
            "Customer Name"
        )

        item = st.text_input(
            "Item"
        )

        problem = st.text_area(
            "Reported Problem"
        )

        date_received = st.date_input(
            "Date Received"
        )

        problem_type = st.selectbox(
            "Problem Type",
            PROBLEM_TYPES
        )

        parts_needed = st.checkbox(
            "Parts Needed"
        )

        notes = st.text_area(
            "Additional Notes"
        )

        submitted = st.form_submit_button(
            "Add Repair Job",
            type="primary"
        )

    if submitted:
        if (
            not customer.strip()
            or not item.strip()
            or not problem.strip()
        ):

            st.warning(
                "Please fill in all required fields."
            )

        else:
            job = tracker.add_job(
                customer.strip(),
                item.strip(),
                problem.strip(),
                date_received.isoformat(),
                notes.strip(),
                problem_type,
                parts_needed
            )

            st.success(
                f"Repair job added successfully! "
                f"Job ID: {job.job_id}"
            )
            st.info(
                f"Saved to: {DATA_FILE}"
            )

# VIEW REPAIR JOBS
elif page == "View Repair Jobs":
    st.header("Repair Jobs")
    if not tracker.jobs:
        st.info(
            "No repair jobs have been added yet."
        )

    else:
        rows = []
        for job in tracker.jobs:
            risk = tracker.calculate_delay_risk(
                job
            )

            rows.append({
                "Job ID": job.job_id,
                "Customer": job.customer_name,
                "Item": job.item,
                "Problem": job.problem,
                "Problem Type": job.problem_type,
                "Status": job.status,
                "Parts Needed": (
                    "Yes"
                    if job.parts_needed
                    else "No"
                ),
                "Delay Risk": (
                    f"{risk['icon']} "
                    f"{risk['level']} "
                    f"({risk['score']})"
                ),
                "Cost": (
                    f"₱{job.cost:,.2f}"
                )
            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# SEARCH JOBS
elif page == "Search Jobs":
    st.header("Search Repair Jobs")
    keyword = st.text_input(
        "Search by Job ID, customer, item, problem, or status"
    )

    results = tracker.search_jobs(
        keyword
    )

    if not results:
        st.warning(
            "No matching repair jobs found."
        )

    else:
        st.write(
            f"Found {len(results)} job(s)."
        )

        for job in results:
            risk = tracker.calculate_delay_risk(
                job
            )

            with st.expander(
                f"{job.job_id} — "
                f"{job.customer_name} — "
                f"{job.status}"
            ):

                st.write(
                    f"**Item:** {job.item}"
                )

                st.write(
                    f"**Problem:** {job.problem}"
                )

                st.write(
                    f"**Problem Type:** "
                    f"{job.problem_type}"
                )

                st.write(
                    f"**Status:** {job.status}"
                )

                st.write(
                    f"**Parts Needed:** "
                    f"{'Yes' if job.parts_needed else 'No'}"
                )

                st.write(
                    f"**Cost:** "
                    f"₱{job.cost:,.2f}"
                )

                st.write(
                    f"**Delay Risk:** "
                    f"{risk['icon']} "
                    f"{risk['level']} "
                    f"({risk['score']}/100)"
                )

                if risk["reasons"]:

                    st.write(
                        "**Risk Factors:**"
                    )

                    for reason in risk["reasons"]:

                        st.write(
                            f"- {reason}"
                        )


# UPDATE JOB
elif page == "Update Job":
    st.header("Update Repair Job")
    if not tracker.jobs:
        st.info(
            "Add a repair job first."
        )

    else:
        selected = st.selectbox(
            "Select Job ID",
            [
                job.job_id
                for job in tracker.jobs
            ]
        )

        job = tracker.get_job(
            selected
        )

        # Current risk
        current_risk = (
            tracker.calculate_delay_risk(job)
        )

        st.info(
            f"Current Delay Risk: "
            f"{current_risk['icon']} "
            f"{current_risk['level']} "
            f"({current_risk['score']}/100)"
        )

        if current_risk["reasons"]:
            st.write("**Risk Factors:**")
            for reason in current_risk["reasons"]:
                st.write(
                    f"- {reason}"
                )

        st.divider()
        customer = st.text_input(
            "Customer Name",
            value=job.customer_name
        )

        item = st.text_input(
            "Item",
            value=job.item
        )

        problem = st.text_area(
            "Problem",
            value=job.problem
        )

        status = st.selectbox(
            "Repair Status",
            STATUSES,
            index=STATUSES.index(
                job.status
            )
        )

        problem_type = st.selectbox(
            "Problem Type",
            PROBLEM_TYPES,
            index=(
                PROBLEM_TYPES.index(
                    job.problem_type
                )
                if job.problem_type
                in PROBLEM_TYPES
                else 0
            )
        )

        parts_needed = st.checkbox(
            "Parts Needed",
            value=job.parts_needed
        )

        date_received = st.date_input(
            "Date Received",
            value=(
                pd.to_datetime(
                    job.date_received
                ).date()
                if job.date_received
                else pd.Timestamp.today().date()
            )
        )

        cost = st.number_input(
            "Repair Cost (₱)",
            min_value=0.0,
            value=float(job.cost),
            step=50.0
        )

        notes = st.text_area(
            "Notes",
            value=job.notes
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Save Updates",
                type="primary"
            ):

                tracker.update_job(
                    selected,
                    customer.strip(),
                    item.strip(),
                    problem.strip(),
                    status,
                    cost,
                    date_received.isoformat(),
                    "",
                    notes.strip(),
                    problem_type,
                    parts_needed
                )

                st.success(
                    f"{selected} updated successfully."
                )

                st.rerun()

        with col2:
            if st.button(
                "Delete Job",
                type="secondary"
            ):

                if tracker.delete_job(
                    selected
                ):

                    st.success(
                        f"{selected} deleted successfully."
                    )

                    # Refresh dashboard counters
                    st.rerun()