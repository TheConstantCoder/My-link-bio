from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)
links = [
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com"},
    {"name": "YouTube", "url": "https://www.youtube.com"},
]


@app.route("/")
def index():
    return render_template("index.html", links=links)


@app.route("/add", methods=["POST"])
def add_link():
    site_name = request.form.get("site_name", "").strip()
    url = request.form.get("url", "").strip()

    if site_name and url:
        duplicate_exists = any(
            link["name"].lower() == site_name.lower() and link["url"].lower() == url.lower()
            for link in links
        )

        if not duplicate_exists:
            links.append({"name": site_name, "url": url})

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
