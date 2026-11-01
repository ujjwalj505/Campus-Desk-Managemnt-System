import json
from html import escape
from pathlib import Path
from abc import ABC, abstractmethod

import streamlit as st

# ------------------------------------------------------------------
#  Page setup
# ------------------------------------------------------------------
st.set_page_config(page_title="Campus Desk", page_icon="🎓", layout="wide")

# Palette: Midnight Indigo / Violet / Marigold / Mint on a soft lavender paper
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root{
  --ink:#14123A; --indigo:#2D2A7B; --violet:#6C5CE7;
  --marigold:#FFB627; --mint:#2EC4B6; --coral:#FF6B81; --paper:#F5F3FF;
}
html, body, .stApp, p, label, input, textarea, button, li,
[data-testid="stMarkdownContainer"]{
  font-family:'Plus Jakarta Sans',sans-serif;
}
.stApp{ background:var(--paper); }
h1,h2,h3,.hero h1,.section-title{ font-family:'Fraunces',serif !important; color:var(--ink); }
.block-container{ padding-top:2rem; max-width:1150px; }
header[data-testid="stHeader"]{ background:transparent; }

/* Sidebar */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#14123A 0%,#2D2A7B 100%);
}
[data-testid="stSidebar"] *{ color:#EDEBFF; }
.brand{ font-family:'Fraunces',serif; font-size:1.9rem; font-weight:800; color:#fff; margin-bottom:0; }
.brand span{ color:var(--marigold); }
.brand-sub{ font-size:.85rem; color:#B9B5F5; margin-bottom:1.4rem; }
[data-testid="stSidebar"] [role="radiogroup"] label{
  padding:.55rem .8rem; border-radius:12px; margin-bottom:.2rem; transition:background .15s;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{ background:rgba(255,255,255,.1); }

/* Hero */
.hero{
  background:linear-gradient(120deg,#14123A 0%,#4B3FD1 60%,#6C5CE7 100%);
  border-radius:24px; padding:2.2rem 2.4rem; margin-bottom:1.6rem;
  position:relative; overflow:hidden;
  box-shadow:0 18px 40px -18px rgba(45,42,123,.7);
}
.hero:after{
  content:""; position:absolute; right:-60px; top:-60px; width:240px; height:240px;
  border-radius:50%; background:radial-gradient(circle,var(--marigold) 0%,rgba(255,182,39,0) 70%);
  opacity:.85;
}
.hero h1{ color:#fff !important; font-size:2.5rem; margin:0 0 .3rem 0; font-weight:800; }
.hero p{ color:#D8D5FF; margin:0; font-size:1.05rem; }

/* Stat cards */
.stat{
  background:#fff; border-radius:20px; padding:1.3rem 1.4rem;
  border-left:6px solid var(--violet); box-shadow:0 10px 26px -16px rgba(20,18,58,.45);
}
.stat .label{ color:#6b6890; font-weight:600; font-size:.9rem; }
.stat .value{ font-family:'Fraunces',serif; font-weight:800; font-size:2.6rem; color:var(--ink); line-height:1.1; }
.stat.mint{ border-left-color:var(--mint); }
.stat.gold{ border-left-color:var(--marigold); }
.stat.coral{ border-left-color:var(--coral); }

/* Person cards */
.person{
  background:#fff; border-radius:20px; padding:1.2rem 1.3rem; margin-bottom:1rem;
  box-shadow:0 10px 26px -18px rgba(20,18,58,.5); border-top:5px solid var(--violet);
}
.person.teacher{ border-top-color:var(--mint); }
.avatar{
  width:52px; height:52px; border-radius:16px; display:flex; align-items:center; justify-content:center;
  font-family:'Fraunces',serif; font-weight:800; font-size:1.3rem; color:#fff;
  background:linear-gradient(135deg,var(--violet),var(--indigo)); margin-bottom:.7rem;
}
.person.teacher .avatar{ background:linear-gradient(135deg,var(--mint),#1b8f85); }
.person .name{ font-weight:700; font-size:1.1rem; color:var(--ink); }
.person .meta{ color:#6b6890; font-size:.88rem; line-height:1.6; }
.pill{
  display:inline-block; padding:.15rem .7rem; border-radius:999px; font-size:.78rem; font-weight:700;
  background:#EFEBFF; color:var(--indigo); margin-top:.5rem; margin-right:.3rem;
}
.pill.gold{ background:#FFF1CF; color:#8a5b00; }
.pill.mint{ background:#D9F6F3; color:#0f6a62; }

.tip{
  background:#FFF6DD; border-radius:18px; padding:1.1rem 1.3rem; color:#6b4a00;
  border:1px dashed var(--marigold);
}

/* Forms & buttons */
[data-testid="stForm"]{
  background:#fff; border-radius:22px; border:none; padding:1.6rem;
  box-shadow:0 12px 30px -20px rgba(20,18,58,.55);
}
.stButton button, [data-testid="stFormSubmitButton"] button{
  background:linear-gradient(120deg,var(--marigold),#FF9F1C); color:var(--ink);
  border:none; border-radius:14px; padding:.6rem 1.5rem; font-weight:700;
  transition:transform .15s, box-shadow .15s;
}
.stButton button:hover, [data-testid="stFormSubmitButton"] button:hover{
  transform:translateY(-2px); box-shadow:0 10px 20px -10px rgba(255,159,28,.9); color:var(--ink);
}
.stTextInput input, .stNumberInput input{ border-radius:12px !important; }
.stTabs [data-baseweb="tab"]{ font-weight:700; }
.stTabs [aria-selected="true"]{ color:var(--violet); }
.stProgress > div > div > div > div{ background:linear-gradient(90deg,var(--mint),var(--violet)); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
#  Data layer (same school_data.json file and format as before)
# ------------------------------------------------------------------
DATABASE = "school_data.json"


def load():
    data = {"students": [], "teachers": []}
    if Path(DATABASE).exists():
        content = Path(DATABASE).read_text()
        if content.strip():
            data = json.loads(content)
    data.setdefault("students", [])
    data.setdefault("teachers", [])
    return data


def save(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


def next_id(records, key):
    """max + 1, so IDs never repeat after someone is deleted."""
    return max((r.get(key, 0) for r in records), default=0) + 1


# ------------------------------------------------------------------
#  OOP layer (abstract base class + Student / Teacher)
# ------------------------------------------------------------------
class Person(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @abstractmethod
    def register(self, name, age, email):
        pass

    @abstractmethod
    def find(self, name):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and email.endswith(".com")


class Student(Person):
    def get_role(self):
        return "student"

    def register(self, name, age, email):
        data = load()
        if not name.strip():
            return False, "Please enter a name."
        if not Person.validate_email(email):
            return False, "Email is invalid. Use a format like name@example.com"
        roll_no = next_id(data["students"], "roll_no")
        data["students"].append(
            {"name": name.strip(), "age": int(age), "email": email.strip(), "roll_no": roll_no}
        )
        save(data)
        return True, f"{name.strip()} registered successfully with roll no. {roll_no}"

    def find(self, name):
        name = name.strip().lower()
        return [s for s in load()["students"] if name in s["name"].strip().lower()]


class Teacher(Person):
    def get_role(self):
        return "teacher"

    def register(self, name, age, email):
        data = load()
        if not name.strip():
            return False, "Please enter a name."
        if not Person.validate_email(email):
            return False, "Email is invalid. Use a format like name@example.com"
        emp_id = next_id(data["teachers"], "emp_id")
        data["teachers"].append(
            {"name": name.strip(), "age": int(age), "email": email.strip(), "emp_id": emp_id}
        )
        save(data)
        return True, f"{name.strip()} registered successfully with employee ID {emp_id}"

    def find(self, name):
        name = name.strip().lower()
        return [t for t in load()["teachers"] if name in t["name"].strip().lower()]


student_mgr = Student()
teacher_mgr = Teacher()


# ------------------------------------------------------------------
#  UI helpers
# ------------------------------------------------------------------
def hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def stat(label, value, tone=""):
    st.markdown(
        f'<div class="stat {tone}"><div class="label">{escape(label)}</div>'
        f'<div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def grade_letter(p):
    for cutoff, letter in [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (40, "D")]:
        if p >= cutoff:
            return letter
    return "F"


def person_card(p, kind):
    initial = escape(p["name"][:1].upper() or "?")
    if kind == "student":
        ident = f'<span class="pill">Roll #{p.get("roll_no", "-")}</span>'
        g = p.get("grades")
        if isinstance(g, (int, float)):
            ident += f'<span class="pill gold">{g}% · Grade {grade_letter(g)}</span>'
        else:
            ident += '<span class="pill gold">No grades yet</span>'
        cls = "person"
    else:
        ident = f'<span class="pill mint">Emp ID #{p.get("emp_id", "-")}</span>'
        cls = "person teacher"
    st.markdown(
        f"""<div class="{cls}">
              <div class="avatar">{initial}</div>
              <div class="name">{escape(p["name"])}</div>
              <div class="meta">Age {p["age"]}<br>{escape(p["email"])}</div>
              {ident}
            </div>""",
        unsafe_allow_html=True,
    )


def cards_grid(records, kind):
    if not records:
        st.info("Nothing here yet. Register someone to see them listed.")
        return
    cols = st.columns(3)
    for i, rec in enumerate(records):
        with cols[i % 3]:
            person_card(rec, kind)


# ------------------------------------------------------------------
#  Sidebar navigation
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">Campus<span>Desk</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">School management made simple</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["🏠  Dashboard", "➕  Register", "🔎  Directory", "📝  Grades", "🗑️  Remove"],
        label_visibility="collapsed",
    )

data = load()

# ------------------------------------------------------------------
#  Pages
# ------------------------------------------------------------------
if page.startswith("🏠"):
    hero("Welcome back 👋", "Here is a quick look at your school today.")
    graded = [s["grades"] for s in data["students"] if isinstance(s.get("grades"), (int, float))]
    avg = f"{sum(graded) / len(graded):.1f}%" if graded else "-"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat("Students", len(data["students"]))
    with c2:
        stat("Teachers", len(data["teachers"]), "mint")
    with c3:
        stat("Graded students", len(graded), "gold")
    with c4:
        stat("Average score", avg, "coral")

    st.markdown("### Recently added students")
    cards_grid(data["students"][-3:][::-1], "student")

elif page.startswith("➕"):
    hero("Register someone new", "Add a student or a teacher to the school record.")
    tab_s, tab_t = st.tabs(["🎒 Student", "🍎 Teacher"])

    for tab, mgr, label in [(tab_s, student_mgr, "student"), (tab_t, teacher_mgr, "teacher")]:
        with tab:
            left, right = st.columns([3, 2])
            with left:
                with st.form(f"form_{label}", clear_on_submit=True):
                    name = st.text_input("Full name", key=f"n_{label}")
                    age = st.number_input("Age", min_value=3, max_value=100, value=16, key=f"a_{label}")
                    email = st.text_input("Email", placeholder="name@example.com", key=f"e_{label}")
                    submitted = st.form_submit_button(f"Register {label}")
                if submitted:
                    ok, msg = mgr.register(name, age, email)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.balloons()
            with right:
                st.markdown(
                    '<div class="tip"><b>Good to know</b><br>'
                    "Emails must contain @ and end with .com. "
                    "IDs are generated automatically and never repeat, even after deletions.</div>",
                    unsafe_allow_html=True,
                )

elif page.startswith("🔎"):
    hero("Directory", "Search students and teachers, and open their details.")
    query = st.text_input("Search by name", placeholder="Start typing a name…")
    tab_s, tab_t = st.tabs(["🎒 Students", "🍎 Teachers"])
    with tab_s:
        cards_grid(student_mgr.find(query), "student")
    with tab_t:
        cards_grid(teacher_mgr.find(query), "teacher")

elif page.startswith("📝"):
    hero("Grades", "Record the percentage a student has achieved.")
    if not data["students"]:
        st.info("Register a student first, then come back to add grades.")
    else:
        options = {f'{s["name"]} (Roll #{s["roll_no"]})': s["roll_no"] for s in data["students"]}
        left, right = st.columns([3, 2])
        with left:
            choice = st.selectbox("Student", list(options.keys()))
            current = next(s for s in data["students"] if s["roll_no"] == options[choice])
            existing = current.get("grades", 0)
            existing = existing if isinstance(existing, (int, float)) else 0
            with st.form("grade_form"):
                percent = st.slider("Percentage achieved", 0, 100, int(existing))
                go = st.form_submit_button("Save grade")
            if go:
                for s in data["students"]:
                    if s["roll_no"] == options[choice]:
                        s["grades"] = percent
                save(data)
                st.toast(f"Saved {percent}% for {current['name']}", icon="✅")
                st.rerun()
        with right:
            shown = existing
            st.markdown(f"#### {escape(current['name'])}")
            st.progress(min(max(int(shown), 0), 100) / 100)
            st.markdown(
                f'<span class="pill gold">Current: {shown}% · Grade {grade_letter(shown)}</span>',
                unsafe_allow_html=True,
            )

else:
    hero("Remove a record", "Delete a student or teacher. This cannot be undone.")
    who = st.radio("Who do you want to remove?", ["Student", "Teacher"], horizontal=True)
    key = "students" if who == "Student" else "teachers"
    id_key = "roll_no" if who == "Student" else "emp_id"
    records = data[key]
    if not records:
        st.info(f"There are no {key} to remove.")
    else:
        options = {f'{r["name"]} (#{r.get(id_key, "-")})': r.get(id_key) for r in records}
        picked = st.selectbox(f"Select {who.lower()}", list(options.keys()))
        sure = st.checkbox("I understand this will permanently delete the record")
        if st.button(f"Delete {who.lower()}", disabled=not sure):
            target = options[picked]
            data[key] = [r for r in records if r.get(id_key) != target]
            save(data)
            st.toast(f"{picked} has been deleted", icon="🗑️")
            st.rerun()