@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    t = Task.query.get_or_404(task_id)
    projects = Project.query.all()
    if request.method == "POST":
        t.name = request.form["name"]
        t.assignee = request.form["assignee"]
        t.project_id = request.form["project_id"]
        t.priority = request.form["priority"]
        t.status = request.form["status"]
        t.image = request.form["image"]
        t.description = request.form["description"]
        db.session.commit()
        flash("Task updated!")
        return redirect(url_for("project_detail", project_id=t.project_id))
    return render_template("task_form.html", priorities=PRIORITIES, statuses=STATUSES,
                           task=t, projects=projects, project=None, back_url=url_for("projects"))
