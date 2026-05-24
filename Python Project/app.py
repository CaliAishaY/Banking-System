from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("project.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        print(name)
        print(email)
        print(message)

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)