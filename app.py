import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (PREMIUM UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; color: #0f172a; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #3b82f6;
    }
    div[data-testid="metric-container"] > div { color: #64748b !important; font-size: 1.1rem; }
    div[data-testid="metric-container"] label { color: #1e293b !important; font-size: 2.2rem !important; font-weight: 700 !important; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 700 !important; }
    hr { border-color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { background-color: #e0f2fe; border-bottom: 2px solid #0284c7; }
</style>
""", unsafe_allow_html=True)


# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("HR_Analytics_Extended_Data.xlsx")
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


df = load_data()

if df is None or df.empty:
    st.error("❌ Cannot load Excel files. Please ensure your data files are in the folder.")
    st.stop()


# Clean up column names internally if needed, but we will assume standard names exist based on previous inspections.
def get_col(options):
    for opt in options:
        if opt in df.columns: return opt
    return None


attr_col = get_col(['Attrition'])
dept_col = get_col(['Department'])
role_col = get_col(['Job Role'])
age_col = get_col(['Age'])
salary_col = get_col(['Monthly Income', 'Salary'])
gender_col = get_col(['Gender'])
edu_col = get_col(['Education Field', 'Education'])
marital_col = get_col(['Marital Status'])
sat_col = get_col(['Job Satisfaction'])
perf_col = get_col(['Performance Rating'])
wl_col = get_col(['Work Life Balance'])
yac_col = get_col(['Years At Company'])
yslp_col = get_col(['Years Since Last Promotion'])
emp_col = get_col(['emp no', 'Employee Number'])

# --- 7. FILTERS (Interactive) ---
st.sidebar.markdown("## 🎯 Filters")
# Bonus 9: Search Employee
if emp_col:
    search_query = st.sidebar.text_input("🔍 Search Employee (ID)")
else:
    search_query = ""

if dept_col:
    selected_depts = st.sidebar.multiselect("Department", df[dept_col].dropna().unique(),
                                            default=df[dept_col].dropna().unique())
if gender_col:
    selected_genders = st.sidebar.multiselect("Gender", df[gender_col].dropna().unique(),
                                              default=df[gender_col].dropna().unique())
if role_col:
    selected_roles = st.sidebar.multiselect("Job Role", df[role_col].dropna().unique(),
                                            default=df[role_col].dropna().unique())
if age_col:
    min_age, max_age = int(df[age_col].min()), int(df[age_col].max())
    age_range = st.sidebar.slider("Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

# Apply Filters
filtered_df = df.copy()
if search_query and emp_col:
    filtered_df = filtered_df[filtered_df[emp_col].astype(str).str.contains(search_query, case=False)]
if dept_col: filtered_df = filtered_df[filtered_df[dept_col].isin(selected_depts)]
if gender_col: filtered_df = filtered_df[filtered_df[gender_col].isin(selected_genders)]
if role_col: filtered_df = filtered_df[filtered_df[role_col].isin(selected_roles)]
if age_col: filtered_df = filtered_df[(filtered_df[age_col] >= age_range[0]) & (filtered_df[age_col] <= age_range[1])]

# --- HEADER ---
st.title("HR Analytics Dashboard")
st.markdown("---")

# --- 1. BASIC OVERVIEW SECTION (Top KPIs) ---
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

total_emp = len(filtered_df)

attrition_count = 0
attrition_rate = 0.0
if attr_col:
    attr_mask = filtered_df[attr_col].astype(str).str.lower().isin(['yes', 'true', '1', 'y', 'left'])
    attrition_count = attr_mask.sum()
    attrition_rate = (attrition_count / total_emp) * 100 if total_emp > 0 else 0

avg_salary = filtered_df[salary_col].mean() if salary_col else 0
avg_age = filtered_df[age_col].mean() if age_col else 0

gender_ratio = "N/A"
if gender_col:
    g_counts = filtered_df[gender_col].value_counts()
    males = g_counts.get('Male', 0)
    females = g_counts.get('Female', 0)
    total = males + females
    if total > 0:
        gender_ratio = f"{int((males / total) * 100)}% M / {int((females / total) * 100)}% F"

with kpi1: st.metric("👨‍💼 Total Employees", f"{total_emp:,}")
with kpi2: st.metric("🚪 Attrition Count", f"{attrition_count:,}")
with kpi3: st.metric("📉 Attrition Rate", f"{attrition_rate:.1f}%")
with kpi4: st.metric("💰 Average Salary", f"${avg_salary:,.0f}" if pd.notnull(avg_salary) else "N/A")
with kpi5: st.metric("📊 Average Age", f"{avg_age:.1f}" if pd.notnull(avg_age) else "N/A")
with kpi6: st.metric("🧑‍🤝‍🧑 Gender Ratio", gender_ratio)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS FOR ORGANIZED SECTIONS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📉 2. Attrition Analysis",
    "🧑‍🤝‍🧑 3. Demographics",
    "💰 4. Salary & Comp",
    "⭐ 5 & 6. Performance & Tenure"
])

chart_theme = "plotly_white"

with tab1:
    st.subheader("Attrition Insights (HR Focus)")
    if attr_col:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            if dept_col:
                attr_dept = filtered_df[attr_mask][dept_col].value_counts().reset_index()
                attr_dept.columns = [dept_col, 'Attrition Count']
                fig = px.bar(attr_dept, x=dept_col, y='Attrition Count', title="Attrition by Department",
                             color=dept_col, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            if age_col:
                # Bonus 9: Trend line / bins for age
                filtered_df['Age Group'] = pd.cut(filtered_df[age_col], bins=[18, 25, 35, 45, 55, 100],
                                                  labels=['18-25', '26-35', '36-45', '46-55', '55+'])
                attr_age = filtered_df[filtered_df[attr_col].astype(str).str.lower() == 'yes'][
                    'Age Group'].value_counts().reset_index()
                attr_age.columns = ['Age Group', 'Count']
                fig = px.pie(attr_age, names='Age Group', values='Count', title="Attrition by Age Group", hole=0.4,
                             template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)

        with r1c2:
            if role_col:
                attr_role = filtered_df[attr_mask][role_col].value_counts().reset_index()
                attr_role.columns = [role_col, 'Attrition Count']
                fig = px.bar(attr_role, x='Attrition Count', y=role_col, orientation='h', title="Attrition by Job Role",
                             color=role_col, template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            if yac_col:
                attr_yac = filtered_df[attr_mask][yac_col].value_counts().reset_index()
                attr_yac.columns = [yac_col, 'Attrition Count']
                fig = px.bar(attr_yac, x=yac_col, y='Attrition Count', title="Attrition by Years at Company",
                             template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Attrition column not found in dataset.")

with tab2:
    st.subheader("Employee Demographics")
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        if dept_col:
            fig = px.pie(filtered_df, names=dept_col, title="Employees by Department", template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)
        if marital_col:
            fig = px.histogram(filtered_df, x=marital_col, title="Employees by Marital Status", color=marital_col,
                               template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)
    with r2c2:
        if edu_col:
            fig = px.pie(filtered_df, names=edu_col, hole=0.5, title="Employees by Education Field",
                         template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)
        if gender_col:
            fig = px.histogram(filtered_df, x=gender_col, title="Employees by Gender", color=gender_col,
                               template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Salary & Compensation Insights")
    if salary_col:
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            if dept_col:
                sal_dept = filtered_df.groupby(dept_col)[salary_col].mean().reset_index()
                fig = px.bar(sal_dept, x=dept_col, y=salary_col, title="Average Salary by Department", color=dept_col,
                             template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
            if role_col:
                # Professional Box Plot!
                fig = px.box(filtered_df, x=role_col, y=salary_col, color=role_col,
                             title="Salary vs Job Role (Box Plot)", template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)
        with r3c2:
            if yac_col:
                fig = px.scatter(filtered_df, x=yac_col, y=salary_col, color=dept_col if dept_col else None,
                                 title="Salary vs Experience (Years at Company)", template=chart_theme)
                st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Performance & Tenure Analysis")
    r4c1, r4c2 = st.columns(2)
    with r4c1:
        if sat_col and dept_col:
            sat_dept = filtered_df.groupby(dept_col)[sat_col].mean().reset_index()
            fig = px.bar(sat_dept, x=dept_col, y=sat_col, title="Average Satisfaction by Department", color=dept_col,
                         template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)
        if perf_col:
            fig = px.histogram(filtered_df, x=perf_col, title="Performance Rating Distribution", template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)

    with r4c2:
        if yac_col:
            fig = px.histogram(filtered_df, x=yac_col, title="Years at Company Distribution", nbins=15,
                               template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)
        if yslp_col:
            # Line chart for Years since last promotion
            yslp_counts = filtered_df[yslp_col].value_counts().sort_index().reset_index()
            yslp_counts.columns = [yslp_col, 'Count']
            fig = px.line(yslp_counts, x=yslp_col, y='Count', markers=True, title="Years Since Last Promotion",
                          template=chart_theme)
            st.plotly_chart(fig, use_container_width=True)

# --- 9. BONUS FEATURES (Download Report) ---
st.markdown("---")
st.subheader("📊 Data Export")
# Create a CSV download button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data Report (CSV)",
    data=csv,
    file_name='hr_analytics_report.csv',
    mime='text/csv',
)
