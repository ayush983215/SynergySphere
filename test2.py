@app.route("/seed")
def seed():
    if not Project.query.first():
        p1 = Project(name="Website Redesign", topic="UI/UX", manager="Alice",
                     duration="3 months", priority="High", description="Overhaul the company website")
        p2 = Project(name="Mobile App", topic="Development", manager="Bob",
                     duration="6 months", priority="Medium", description="Build customer-facing app")
        db.session.add_all([p1, p2])
        db.session.commit()
        t1 = Task(name="Wireframes", assignee="Charlie", project_id=p1.id,
                  priority="Medium", status="Todo", description="Create initial wireframes")
        t2 = Task(name="Frontend", assignee="Dana", project_id=p1.id,
                  priority="High", status="In Progress", description="Implement designs")
        db.session.add_all([t1, t2])
        db.session.commit()
    flash("Seed data inserted")
    return redirect(url_for("projects"))

# -----------------
# Run
# -----------------
if _name_ == "_main_":
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=5000,debug=True)
