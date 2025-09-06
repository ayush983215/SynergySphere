from flask import Flask, redirect, url_for, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja2 import DictLoader

app = Flask(__name__)
app.secret_key = "devkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------
# Database Models
# -----------------
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    topic = db.Column(db.String(120))
    manager = db.Column(db.String(120))
    duration = db.Column(db.String(120))
    priority = db.Column(db.String(50))
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="project", lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    assignee = db.Column(db.String(120))
    priority = db.Column(db.String(50))
    status = db.Column(db.String(50))
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)

# -----------------
# Templates (Jinja)
# -----------------
BASE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title or 'Projects' }}</title>
  <style>
    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu; margin:0; background:#0b1220; color:#e6e9ef}
    a{color:#8ab4ff; text-decoration:none}
    a:hover{text-decoration:underline}
    .container{max-width:1100px; margin:0 auto; padding:24px}
    .nav{display:flex; gap:12px; align-items:center; padding:16px 0}
    .btn{display:inline-block; padding:10px 14px; border-radius:12px; background:#2b3345; color:#e6e9ef}
    .btn:hover{background:#3a4258}
    .btn.primary{background:#5b8cff}
    .btn.primary:hover{background:#4a79e5}
    .grid{display:grid; gap:16px}
    .grid-3{grid-template-columns:repeat(3,minmax(0,1fr))}
    .card{background:#12192b; border:1px solid #1f2740; border-radius:18px; overflow:hidden}
    .card .body{padding:16px}
    .muted{color:#a0a7b7}
    .row{display:flex; gap:12px; align-items:center}
    input,select,textarea{background:#0e1526; color:#e6e9ef; border:1px solid #263250; padding:10px 12px; border-radius:12px; width:100%}
    label{font-size:12px; color:#a0a7b7}
    .field{display:grid; gap:6px}
    form .grid-2{grid-template-columns:repeat(2,minmax(0,1fr))}
    .badge{padding:4px 10px; border-radius:999px; border:1px solid #2f3b5f; font-size:12px}
    .footer{margin-top:24px; display:flex; gap:8px; align-items:center}
    img.thumb{width:100%; height:140px; object-fit:cover; display:block}
    .kanban{display:grid; grid-template-columns:repeat(3,1fr); gap:16px}
    .col{background:#0e1526; border-radius:14px; padding:12px; border:1px solid #1f2740}
    .task{background:#12192b; border:1px solid #293456; border-radius:14px; padding:12px; margin-bottom:10px}
    .flash{background:#173155; border:1px solid #2b4a7a; padding:10px 12px; border-radius:12px; margin:8px 0}
  </style>
</head>
<body>
  <div class="container">
    <div class="nav">
      <a class="btn" href="{{ url_for('projects') }}">Projects</a>
      <a class="btn" href="{{ url_for('my_tasks') }}">My Tasks</a>
      <div class="muted" style="margin-left:auto">Demo user — no login needed</div>
    </div>
    {% for m in get_flashed_messages() %}
      <div class="flash">{{ m }}</div>
    {% endfor %}
    {% block content %}{% endblock %}
  </div>
</body>
</html>
"""

PROJECTS_TMPL = r"""{% extends "base.html" %}{% block content %}
<h2>Projects</h2>
<a href="{{ url_for('new_project') }}" class="btn primary">+ New Project</a>
<div class="grid grid-3" style="margin-top:16px">
  {% for p in projects %}
    <div class="card">
      {% if p.image %}<img src="{{ p.image }}" class="thumb">{% endif %}
      <div class="body">
        <h3><a href="{{ url_for('project_detail', project_id=p.id) }}">{{ p.name }}</a></h3>
        <div class="muted">{{ p.topic }}</div>
        <div class="footer">
          <span class="badge">{{ p.priority }}</span>
          <a class="btn" href="{{ url_for('edit_project', project_id=p.id) }}">Edit</a>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
{% endblock %}"""

PROJECT_DETAIL_TMPL = r"""{% extends "base.html" %}{% block content %}
<h2>{{ project.name }}</h2>
<div class="muted">{{ project.description }}</div>
<a href="{{ url_for('new_task', project_id=project.id) }}" class="btn primary">+ New Task</a>
<div class="kanban" style="margin-top:20px">
  {% for status, tasks in tasks_by.items() %}
    <div class="col">
      <h4>{{ status }}</h4>
      {% for t in tasks %}
        <div class="task">
          <b>{{ t.name }}</b><br>
          <span class="muted">{{ t.assignee }}</span>
          <div class="footer">
            <span class="badge">{{ t.priority }}</span>
            <a class="btn" href="{{ url_for('edit_task', task_id=t.id) }}">Edit</a>
          </div>
        </div>
      {% endfor %}
    </div>
  {% endfor %}
</div>
{% endblock %}"""

MY_TASKS_TMPL = r"""{% extends "base.html" %}{% block content %}
<h2>My Tasks</h2>
<div class="grid grid-3">
  {% for t in tasks %}
    <div class="card">
      <div class="body">
        <b>{{ t.name }}</b>
        <div class="muted">{{ t.project.name }}</div>
        <div class="footer">
          <span class="badge">{{ t.status }}</span>
          <span class="badge">{{ t.priority }}</span>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
{% endblock %}"""

PROJECT_FORM_TMPL = r"""{% extends "base.html" %}{% block content %}
<h2>{{ 'Edit' if project else 'New' }} Project</h2>
<form method="post" class="grid grid-2">
  <div class="field"><label>Name</label><input name="name" value="{{ project.name if project else '' }}"></div>
  <div class="field"><label>Topic</label><input name="topic" value="{{ project.topic if project else '' }}"></div>
  <div class="field"><label>Manager</label><input name="manager" value="{{ project.manager if project else '' }}"></div>
  <div class="field"><label>Duration</label><input name="duration" value="{{ project.duration if project else '' }}"></div>
  <div class="field"><label>Priority</label>
    <select name="priority">{% for p in priorities %}
      <option value="{{p}}" {% if project and project.priority==p %}selected{% endif %}>{{p}}</option>
    {% endfor %}</select>
  </div>
  <div class="field"><label>Image URL</label><input name="image" value="{{ project.image if project else '' }}"></div>
  <div class="field" style="grid-column: span 2"><label>Description</label><textarea name="description">{{ project.description if project else '' }}</textarea></div>
  <div style="grid-column: span 2"><button class="btn primary">Save</button></div>
</form>
{% endblock %}"""

TASK_FORM_TMPL = r"""{% extends "base.html" %}{% block content %}
<h2>{{ 'Edit' if task else 'New' }} Task</h2>
<form method="post" class="grid grid-2">
  <div class="field"><label>Name</label><input name="name" value="{{ task.name if task else '' }}"></div>
  <div class="field"><label>Assignee</label><input name="assignee" value="{{ task.assignee if task else '' }}"></div>
  <div class="field"><label>Project</label>
    <select name="project_id">
      {% for p in projects %}
        <option value="{{p.id}}" {% if project and project.id==p.id %}selected{% elif task and task.project_id==p.id %}selected{% endif %}>{{p.name}}</option>
      {% endfor %}
    </select>
  </div>
  <div class="field"><label>Status</label>
    <select name="status">{% for s in statuses %}
      <option value="{{s}}" {% if task and task.status==s %}selected{% endif %}>{{s}}</option>
    {% endfor %}</select>
  </div>
  <div class="field"><label>Priority</label>
    <select name="priority">{% for p in priorities %}
      <option value="{{p}}" {% if task and task.priority==p %}selected{% endif %}>{{p}}</option>
    {% endfor %}</select>
  </div>
  <div class="field"><label>Image URL</label><input name="image" value="{{ task.image if task else '' }}"></div>
  <div class="field" style="grid-column: span 2"><label>Description</label><textarea name="description">{{ task.description if task else '' }}</textarea></div>
  <div style="grid-column: span 2"><button class="btn primary">Save</button></div>
</form>
{% endblock %}"""

# Register templates
app.jinja_loader = DictLoader({
    "base.html": BASE,
    "projects.html": PROJECTS_TMPL,
    "project_detail.html": PROJECT_DETAIL_TMPL,
    "my_tasks.html": MY_TASKS_TMPL,
    "project_form.html": PROJECT_FORM_TMPL,
    "task_form.html": TASK_FORM_TMPL,
})

# -----------------
# Routes
# -----------------
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Todo", "In Progress", "Done"]

@app.route("/")
def home():
    return redirect(url_for("projects"))

@app.route("/projects")
def projects():
    ps = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects.html", title="Projects", projects=ps)

@app.route("/project/<int:project_id>")
def project_detail(project_id: int):
    p = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.created_at.desc()).all()
    tasks_by = {s: [t for t in tasks if t.status == s] for s in STATUSES}
    return render_template("project_detail.html", title=p.name, project=p, tasks_by=tasks_by)

@app.route("/my_tasks")
def my_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("my_tasks.html", title="My Tasks", tasks=tasks)

@app.route("/projects/new", methods=["GET", "POST"])
def new_project():
    if request.method == "POST":
        p = Project(
            name=request.form["name"],
            topic=request.form["topic"],
            manager=request.form["manager"],
            duration=request.form["duration"],
            priority=request.form["priority"],
            image=request.form["image"],
            description=request.form["description"],
        )
        db.session.add(p)
        db.session.commit()
        flash("Project created!")
        return redirect(url_for("projects"))
    return render_template("project_form.html", priorities=PRIORITIES, project=None)

@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    p = Project.query.get_or_404(project_id)
    if request.method == "POST":
        p.name = request.form["name"]
        p.topic = request.form["topic"]
        p.manager = request.form["manager"]
        p.duration = request.form["duration"]
        p.priority = request.form["priority"]
        p.image = request.form["image"]
        p.description = request.form["description"]
        db.session.commit()
        flash("Project updated!")
        return redirect(url_for("projects"))
    return render_template("project_form.html", priorities=PRIORITIES, project=p)

@app.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    projects = Project.query.all()
    project_id = request.args.get("project_id", type=int)
    selected = Project.query.get(project_id) if project_id else None
    if request.method == "POST":
        t = Task(
            name=request.form["name"],
            assignee=request.form["assignee"],
            project_id=request.form["project_id"],
            priority=request.form["priority"],
            status=request.form["status"],
            image=request.form["image"],
            description=request.form["description"],
        )
        db.session.add(t)
        db.session.commit()
        flash("Task created!")
        return redirect(url_for("project_detail", project_id=t.project_id))
    return render_template("task_form.html", priorities=PRIORITIES, statuses=STATUSES,
                           task=None, projects=projects, project=selected, back_url=url_for("projects"))
