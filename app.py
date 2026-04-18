from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request, url_for
import requests


app = Flask(__name__)


def get_og_content(soup, property_name):
    tag = soup.find("meta", property=property_name)
    if tag and tag.get("content"):
        return tag["content"].strip()
    return "not available"


def build_link(site_name, url):
    metadata = {
        "title": "not available",
        "description": "not available",
        "image_url": "not available",
    }

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        metadata = {
            "title": get_og_content(soup, "og:title"),
            "description": get_og_content(soup, "og:description"),
            "image_url": get_og_content(soup, "og:image"),
        }
    except requests.RequestException:
        pass

    return {
        "name": site_name,
        "url": url,
        "title": metadata["title"],
        "description": metadata["description"],
        "image_url": metadata["image_url"],
    }


links = [
    build_link("GitHub", "https://github.com"),
    build_link("LinkedIn", "https://www.linkedin.com"),
    build_link("YouTube", "https://www.youtube.com"),
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
            links.append(build_link(site_name, url))

    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete_link():
    link_index = request.form.get("link_index", "").strip()

    if link_index.isdigit():
        index = int(link_index)
        if 0 <= index < len(links):
            del links[index]

    return redirect(url_for("index"))


@app.route("/edit/<int:link_index>")
def edit_link(link_index):
    if 0 <= link_index < len(links):
        return render_template("edit.html", link=links[link_index], link_index=link_index)

    return redirect(url_for("index"))


@app.route("/update/<int:link_index>", methods=["POST"])
def update_link(link_index):
    if 0 <= link_index < len(links):
        site_name = request.form.get("site_name", "").strip()
        url = request.form.get("url", "").strip()

        if site_name and url:
            duplicate_exists = any(
                current_index != link_index
                and link["name"].lower() == site_name.lower()
                and link["url"].lower() == url.lower()
                for current_index, link in enumerate(links)
            )

            if not duplicate_exists:
                links[link_index] = build_link(site_name, url)

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
