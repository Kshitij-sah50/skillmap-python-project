"""
SkillMap - Career Readiness & Skill Gap Analyzer
Mini Project | Python (Dictionaries, Classes, Functions, Pandas, Plotly, Tkinter)

Everything works inside ONE window:
  Summary tab   -> match %, readiness level, matched / missing skills
  Roadmap tab   -> step-by-step learning plan table
  Charts tab    -> role comparison bar chart + skill gap pie (embedded)
  All Roles tab -> Pandas table comparing every role

Install:  pip install pandas plotly matplotlib
Run:      python skillmap.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import plotly.express as px
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------------
# 1. DATA (Dictionaries)
# ---------------------------------------------------------------

# Job role -> list of required skills
JOB_ROLES = {
    "Data Analyst": ["Python", "SQL", "Excel", "Pandas", "NumPy",
                     "Matplotlib", "Statistics", "Power BI"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "Python", "Flask",
                      "SQL", "Git", "React"],
    "Data Scientist": ["Python", "Statistics", "Pandas", "NumPy",
                       "Machine Learning", "SQL", "Matplotlib", "Plotly"],
    "Software Engineer": ["Python", "Data Structures", "Algorithms", "Git",
                          "SQL", "OOP", "Testing", "Linux"],
    "Cloud Engineer": ["Linux", "Networking", "AWS", "Docker", "Python",
                       "Git", "SQL", "Security"],
}

# Skill -> (learning resource, estimated hours to learn)
LEARNING = {
    "Python": ("Python.org tutorial / CS50P", 40),
    "SQL": ("SQLZoo / Mode SQL tutorial", 25),
    "Excel": ("Microsoft Excel training videos", 20),
    "Pandas": ("Pandas official 10-minute guide", 20),
    "NumPy": ("NumPy beginner's guide", 15),
    "Matplotlib": ("Matplotlib pyplot tutorial", 10),
    "Statistics": ("Khan Academy Statistics", 30),
    "Power BI": ("Microsoft Learn Power BI", 25),
    "HTML": ("MDN HTML basics", 10),
    "CSS": ("MDN CSS basics", 15),
    "JavaScript": ("javascript.info", 40),
    "Flask": ("Flask official quickstart", 15),
    "Git": ("Git book (Pro Git)", 10),
    "React": ("react.dev learn", 35),
    "Machine Learning": ("Andrew Ng ML course", 60),
    "Plotly": ("Plotly Express documentation", 8),
    "Data Structures": ("GeeksforGeeks DSA course", 50),
    "Algorithms": ("CLRS / NeetCode roadmap", 50),
    "OOP": ("Python OOP tutorial", 15),
    "Testing": ("pytest documentation", 10),
    "Linux": ("Linux Journey", 20),
    "Networking": ("Computer Networking basics (Cisco)", 25),
    "AWS": ("AWS Cloud Practitioner course", 30),
    "Docker": ("Docker getting started", 12),
    "Security": ("OWASP Top 10 guide", 20),
}

ALL_SKILLS = sorted(LEARNING)      # every skill the user can tick
HOURS_PER_WEEK = 10                # used for the roadmap timeline

# Colours used in the GUI
BG = "#f4f6fb"
PRIMARY = "#1e3a8a"
GREEN = "#2e7d32"
ORANGE = "#ef6c00"
RED = "#c62828"
GREY = "#9fb3d1"


# ---------------------------------------------------------------
# 2. CLASS
# ---------------------------------------------------------------

class Student:
    """Stores a student's name and skills."""

    def __init__(self, name, skills):
        self.name = name
        self.skills = skills       # list of skill names


# ---------------------------------------------------------------
# 3. FUNCTIONS (analysis logic)
# ---------------------------------------------------------------

def analyze_role(student, role):
    """Compare a student against one role. Returns a dictionary."""
    required = JOB_ROLES[role]
    matched = [s for s in required if s in student.skills]
    missing = [s for s in required if s not in student.skills]
    percent = round(len(matched) / len(required) * 100, 1)
    return {"role": role, "matched": matched,
            "missing": missing, "percent": percent}


def readiness_level(percent):
    """Simple if / elif / else label."""
    if percent >= 80:
        return "Job Ready"
    elif percent >= 50:
        return "Almost There"
    else:
        return "Needs Work"


def level_color(percent):
    """Colour that goes with the readiness level."""
    if percent >= 80:
        return GREEN
    elif percent >= 50:
        return ORANGE
    else:
        return RED


def analyze_all_roles(student):
    """Analyze every role and return a Pandas DataFrame, best match first."""
    rows = []
    for role in JOB_ROLES:
        r = analyze_role(student, role)
        rows.append({"Role": role,
                     "Match %": r["percent"],
                     "Matched": len(r["matched"]),
                     "Missing": len(r["missing"]),
                     "Level": readiness_level(r["percent"])})
    df = pd.DataFrame(rows)
    return df.sort_values("Match %", ascending=False).reset_index(drop=True)


def build_roadmap(missing):
    """Turn missing skills into a step-by-step learning plan (list of dicts)."""
    roadmap = []
    total_hours = 0
    for step, skill in enumerate(missing, start=1):
        resource, hours = LEARNING[skill]
        total_hours += hours
        roadmap.append({"step": step, "skill": skill, "resource": resource,
                        "hours": hours,
                        "done_by_week": round(total_hours / HOURS_PER_WEEK)})
    return roadmap


# ---------------------------------------------------------------
# 4. GUI (Tkinter) - everything in one window
# ---------------------------------------------------------------

class SkillMapApp:
    def __init__(self, root):
        self.root = root
        root.title("SkillMap - Career Readiness & Skill Gap Analyzer")
        root.geometry("1150x700")
        root.minsize(1000, 620)
        root.configure(bg=BG)

        self.student = None
        self.result = None
        self.skill_vars = {}       # skill -> IntVar (checkbox state)

        self.setup_style()
        self.build_header()
        self.build_body()
        self.build_status_bar()

    # ---------- look and feel ----------
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", padding=(16, 6), font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background=PRIMARY, foreground="white")
        style.configure("Bar.Horizontal.TProgressbar", troughcolor="#dde3f0",
                        background=GREEN, thickness=18)

    def build_header(self):
        header = tk.Frame(self.root, bg=PRIMARY)
        header.pack(fill="x")
        tk.Label(header, text="SkillMap", font=("Segoe UI", 22, "bold"),
                 bg=PRIMARY, fg="white").pack(side="left", padx=18, pady=8)
        tk.Label(header, text="Career Readiness & Skill Gap Analyzer",
                 font=("Segoe UI", 11), bg=PRIMARY, fg="#c7d2fe").pack(side="left", pady=8)

    def build_status_bar(self):
        self.status = tk.Label(self.root, text="Enter your details and click Analyze.",
                               anchor="w", bg="#dde3f0", font=("Segoe UI", 9), padx=10)
        self.status.pack(fill="x", side="bottom")

    def build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        self.build_left(body)
        self.build_right(body)

    # ---------- left panel: inputs + buttons ----------
    def build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 10))

        # student details
        box1 = tk.LabelFrame(left, text=" Student Details ", bg=BG,
                             font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        box1.pack(fill="x")

        tk.Label(box1, text="Name", bg=BG).grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(box1, width=28)
        self.name_entry.grid(row=0, column=1, pady=3, padx=(8, 0))

        tk.Label(box1, text="Target Role", bg=BG).grid(row=1, column=0, sticky="w")
        self.role_box = ttk.Combobox(box1, values=list(JOB_ROLES),
                                     state="readonly", width=25)
        self.role_box.grid(row=1, column=1, pady=3, padx=(8, 0))

        # skills
        box2 = tk.LabelFrame(left, text=" Your Skills ", bg=BG,
                             font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        box2.pack(fill="x", pady=8)

        grid = tk.Frame(box2, bg=BG)
        grid.pack()
        for i, skill in enumerate(ALL_SKILLS):
            var = tk.IntVar()
            self.skill_vars[skill] = var
            tk.Checkbutton(grid, text=skill, variable=var, bg=BG,
                           activebackground=BG, anchor="w", width=16
                           ).grid(row=i // 2, column=i % 2, sticky="w")

        small = tk.Frame(box2, bg=BG)
        small.pack(pady=(6, 0))
        ttk.Button(small, text="Select All", command=self.select_all).pack(side="left", padx=3)
        ttk.Button(small, text="Deselect All", command=self.deselect_all).pack(side="left", padx=3)

        # action buttons
        tk.Button(left, text="ANALYZE", bg=GREEN, fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2", command=self.analyze
                  ).pack(fill="x", ipady=6)

        row = tk.Frame(left, bg=BG)
        row.pack(fill="x", pady=6)
        ttk.Button(row, text="Save CSV", command=self.save_csv).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(row, text="Plotly Charts", command=self.open_plotly).pack(side="left", expand=True, fill="x", padx=3)
        ttk.Button(row, text="Reset", command=self.reset).pack(side="left", expand=True, fill="x", padx=(3, 0))

    # ---------- right panel: tabs ----------
    def build_right(self, parent):
        tabs = ttk.Notebook(parent)
        tabs.pack(side="left", fill="both", expand=True)
        self.tabs = tabs

        self.build_summary_tab()
        self.build_roadmap_tab()
        self.build_charts_tab()
        self.build_roles_tab()

    def build_summary_tab(self):
        tab = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab, text="  Summary  ")

        self.title_label = tk.Label(tab, text="No analysis yet", bg="white",
                                    font=("Segoe UI", 12), fg="#555")
        self.title_label.pack(pady=(18, 0))

        self.percent_label = tk.Label(tab, text="--%", bg="white",
                                      font=("Segoe UI", 54, "bold"), fg=PRIMARY)
        self.percent_label.pack()

        self.level_label = tk.Label(tab, text="", bg="white", font=("Segoe UI", 14, "bold"))
        self.level_label.pack()

        self.progress = ttk.Progressbar(tab, length=480, maximum=100,
                                        style="Bar.Horizontal.TProgressbar")
        self.progress.pack(pady=12)

        lists = tk.Frame(tab, bg="white")
        lists.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        have_box = tk.LabelFrame(lists, text=" Skills You Have ", bg="white",
                                 fg=GREEN, font=("Segoe UI", 10, "bold"))
        have_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.have_list = tk.Listbox(have_box, font=("Segoe UI", 11), fg=GREEN,
                                    relief="flat", activestyle="none")
        self.have_list.pack(fill="both", expand=True, padx=6, pady=6)

        miss_box = tk.LabelFrame(lists, text=" Skills Missing ", bg="white",
                                 fg=RED, font=("Segoe UI", 10, "bold"))
        miss_box.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.miss_list = tk.Listbox(miss_box, font=("Segoe UI", 11), fg=RED,
                                    relief="flat", activestyle="none")
        self.miss_list.pack(fill="both", expand=True, padx=6, pady=6)

    def build_roadmap_tab(self):
        tab = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab, text="  Learning Roadmap  ")

        self.roadmap_info = tk.Label(tab, text="Click Analyze to generate your roadmap.",
                                     bg="white", font=("Segoe UI", 11, "bold"), fg=PRIMARY)
        self.roadmap_info.pack(anchor="w", padx=15, pady=10)

        columns = ("Step", "Skill", "Resource", "Hours", "Done By Week")
        self.roadmap_tree = ttk.Treeview(tab, columns=columns, show="headings")
        widths = (60, 140, 300, 70, 110)
        for col, w in zip(columns, widths):
            self.roadmap_tree.heading(col, text=col)
            self.roadmap_tree.column(col, width=w, anchor="center" if col != "Resource" else "w")
        self.roadmap_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def build_charts_tab(self):
        tab = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab, text="  Charts  ")

        self.figure = Figure(figsize=(9, 4.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=tab)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def build_roles_tab(self):
        tab = tk.Frame(self.tabs, bg="white")
        self.tabs.add(tab, text="  All Roles  ")

        tk.Label(tab, text="Your match against every job role (best first)",
                 bg="white", font=("Segoe UI", 11, "bold"), fg=PRIMARY
                 ).pack(anchor="w", padx=15, pady=10)

        columns = ("Role", "Match %", "Matched", "Missing", "Level")
        self.roles_tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            self.roles_tree.heading(col, text=col)
            self.roles_tree.column(col, width=130, anchor="center")
        self.roles_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # ---------- small helpers ----------
    def select_all(self):
        for var in self.skill_vars.values():
            var.set(1)

    def deselect_all(self):
        for var in self.skill_vars.values():
            var.set(0)

    def set_status(self, text):
        self.status.config(text=text)

    # ---------- main action ----------
    def analyze(self):
        name = self.name_entry.get().strip()
        role = self.role_box.get()
        skills = [s for s, var in self.skill_vars.items() if var.get() == 1]

        # input validation
        if name == "":
            messagebox.showwarning("Missing", "Please enter your name.")
            return
        if role == "":
            messagebox.showwarning("Missing", "Please select a target role.")
            return
        if len(skills) == 0:
            messagebox.showwarning("Missing", "Please tick at least one skill.")
            return

        self.student = Student(name, skills)
        self.result = analyze_role(self.student, role)

        # update every tab in the same window
        self.update_summary()
        self.update_roadmap()
        self.update_charts()
        self.update_roles_table()

        self.tabs.select(0)
        self.set_status(f"Analysis complete for {name} - target role: {role}")

    # ---------- update each tab ----------
    def update_summary(self):
        percent = self.result["percent"]
        color = level_color(percent)

        self.title_label.config(text=f"{self.student.name}  >  {self.result['role']}")
        self.percent_label.config(text=f"{percent}%", fg=color)
        self.level_label.config(text=readiness_level(percent), fg=color)

        ttk.Style().configure("Bar.Horizontal.TProgressbar", background=color)
        self.progress["value"] = percent

        self.have_list.delete(0, tk.END)
        for skill in self.result["matched"]:
            self.have_list.insert(tk.END, "  " + skill)
        self.miss_list.delete(0, tk.END)
        for skill in self.result["missing"]:
            self.miss_list.insert(tk.END, "  " + skill)

    def update_roadmap(self):
        roadmap = build_roadmap(self.result["missing"])
        self.roadmap_tree.delete(*self.roadmap_tree.get_children())

        for item in roadmap:
            self.roadmap_tree.insert("", tk.END, values=(
                item["step"], item["skill"], item["resource"],
                item["hours"], f"Week {item['done_by_week']}"))

        if len(roadmap) == 0:
            self.roadmap_info.config(text="You already meet every requirement for this role!")
        else:
            total = sum(item["hours"] for item in roadmap)
            weeks = round(total / HOURS_PER_WEEK)
            self.roadmap_info.config(
                text=f"{len(roadmap)} skills to learn  |  {total} hours  |  "
                     f"about {weeks} weeks at {HOURS_PER_WEEK} hrs/week")

    def update_charts(self):
        df = analyze_all_roles(self.student)
        self.figure.clear()

        # bar chart - all roles (selected role highlighted)
        ax1 = self.figure.add_subplot(121)
        colors = [PRIMARY if r == self.result["role"] else GREY for r in df["Role"]]
        ax1.barh(df["Role"], df["Match %"], color=colors)
        ax1.set_xlim(0, 100)
        ax1.invert_yaxis()
        ax1.set_xlabel("Match %")
        ax1.set_title("Match with Each Role")
        for i, value in enumerate(df["Match %"]):
            ax1.text(value + 1, i, f"{value}%", va="center", fontsize=9)

        # pie chart - matched vs missing for the selected role
        ax2 = self.figure.add_subplot(122)
        matched = len(self.result["matched"])
        missing = len(self.result["missing"])
        sizes = [v for v in (matched, missing) if v > 0]
        labels = [l for l, v in (("Matched", matched), ("Missing", missing)) if v > 0]
        colors2 = [c for c, v in ((GREEN, matched), (RED, missing)) if v > 0]
        ax2.pie(sizes, labels=labels, colors=colors2, autopct="%1.0f%%", startangle=90)
        ax2.set_title(f"Skill Gap: {self.result['role']}")

        self.figure.tight_layout()
        self.canvas.draw()

    def update_roles_table(self):
        df = analyze_all_roles(self.student)
        self.roles_tree.delete(*self.roles_tree.get_children())
        for _, row in df.iterrows():
            self.roles_tree.insert("", tk.END, values=(
                row["Role"], f"{row['Match %']}%", row["Matched"],
                row["Missing"], row["Level"]))

    # ---------- other buttons ----------
    def open_plotly(self):
        """Optional: open interactive Plotly charts in the browser."""
        if self.student is None:
            messagebox.showinfo("Info", "Click Analyze first.")
            return
        df = analyze_all_roles(self.student)
        fig = px.bar(df, x="Role", y="Match %", text="Match %", color="Match %",
                     title=f"Role Match for {self.student.name}", range_y=[0, 100])
        fig.show()

        pie_df = pd.DataFrame({
            "Status": ["Matched", "Missing"],
            "Count": [len(self.result["matched"]), len(self.result["missing"])],
        })
        fig2 = px.pie(pie_df, names="Status", values="Count",
                      title=f"Skill Gap for {self.result['role']}")
        fig2.show()

    def save_csv(self):
        if self.student is None:
            messagebox.showinfo("Info", "Click Analyze first.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{self.student.name}_skillmap_report.csv",
            filetypes=[("CSV files", "*.csv")])
        if filename == "":
            return
        analyze_all_roles(self.student).to_csv(filename, index=False)
        self.set_status(f"Report saved: {filename}")
        messagebox.showinfo("Saved", "Report saved successfully.")

    def reset(self):
        self.name_entry.delete(0, tk.END)
        self.role_box.set("")
        self.deselect_all()

        self.title_label.config(text="No analysis yet")
        self.percent_label.config(text="--%", fg=PRIMARY)
        self.level_label.config(text="")
        self.progress["value"] = 0
        self.have_list.delete(0, tk.END)
        self.miss_list.delete(0, tk.END)

        self.roadmap_tree.delete(*self.roadmap_tree.get_children())
        self.roadmap_info.config(text="Click Analyze to generate your roadmap.")
        self.roles_tree.delete(*self.roles_tree.get_children())
        self.figure.clear()
        self.canvas.draw()

        self.student = None
        self.result = None
        self.set_status("Form cleared. Enter your details and click Analyze.")


# ---------------------------------------------------------------
# 5. MAIN
# ---------------------------------------------------------------

if __name__ == "__main__":
    window = tk.Tk()
    SkillMapApp(window)
    window.mainloop()
