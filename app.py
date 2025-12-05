from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
import os
import time
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()  # <-- load .env file

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY environment variable not set! Please set it before running the app.")

app = Flask(__name__)



# 🔐 Simple admin password (change it as you like)
ADMIN_PASSWORD = "pratik123"

# 📂 Excel file paths
DATA_PATH = os.path.join("data", "faculty_data.xlsx")
UPDATED_PATH = os.path.join("data", "faculty_data_updated.xlsx")

# ⏱️ Delay between SerpAPI calls (to be nice to the API)
SLEEP_BETWEEN_CALLS = 1.0   # seconds


# -------------------------------------------------
# Helper functions for Excel
# -------------------------------------------------
def load_faculty_df():
    """Load the Excel file into a DataFrame."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Excel file not found at {DATA_PATH}")
    return pd.read_excel(DATA_PATH)


def save_faculty_df(df, path=DATA_PATH):
    """Save the DataFrame back to Excel."""
    df.to_excel(path, index=False)


# -------------------------------------------------
# SerpAPI: Fetch data for ONE Google Scholar profile
# -------------------------------------------------
def fetch_scholar_data(profile_url, retries=2):
    """
    Fetch citations, h-index, i10-index for one Google Scholar profile via SerpAPI.

    Returns:
        dict  -> { "Name", "Citations", "H-index", "i10-index" }
        None  -> if completely failed
    """
    try:
        if "user=" not in profile_url:
            print(f"❌ Invalid Scholar URL: {profile_url}")
            return None

        # Extract author_id (user parameter)
        user_id = profile_url.split("user=")[1].split("&")[0]

        params = {
            "engine": "google_scholar_author",
            "author_id": user_id,
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }

        for attempt in range(retries):
            try:
                search = GoogleSearch(params)
                results = search.get_dict()

                author = results.get("author", {})
                cited_by = results.get("cited_by", {})
                table = cited_by.get("table", [])

                # Default values
                citations_all = 0
                h_index_all = 0
                i10_index_all = 0

                # ---- table[0] : citations ----
                if len(table) >= 1:
                    cit_dict = table[0].get("citations", {}) or {}
                    citations_all = (
                        cit_dict.get("all")
                        or cit_dict.get("since_2020")
                        or cit_dict.get("since_2019")
                        or 0
                    )

                # ---- table[1] : h_index ----
                if len(table) >= 2:
                    h_dict = table[1].get("h_index", {}) or {}
                    h_index_all = (
                        h_dict.get("all")
                        or h_dict.get("since_2020")
                        or h_dict.get("since_2019")
                        or 0
                    )

                # ---- table[2] : i10_index ----
                if len(table) >= 3:
                    i_dict = table[2].get("i10_index", {}) or {}
                    i10_index_all = (
                        i_dict.get("all")
                        or i_dict.get("since_2020")
                        or i_dict.get("since_2019")
                        or 0
                    )

                name = author.get("name", "Unknown")

                # If everything looks empty, retry
                if name == "Unknown" and citations_all == 0 and h_index_all == 0:
                    print(f"⚠️ Empty data on attempt {attempt+1} for {profile_url}, retrying...")
                    time.sleep(SLEEP_BETWEEN_CALLS)
                    continue

                # Make sure they are ints (and not None)
                citations_all = int(citations_all or 0)
                h_index_all = int(h_index_all or 0)
                i10_index_all = int(i10_index_all or 0)

                print(
                    f"✅ {name} → Cites: {citations_all}, "
                    f"h-index: {h_index_all}, i10-index: {i10_index_all}"
                )

                return {
                    "Name": name,
                    "Citations": citations_all,
                    "H-index": h_index_all,
                    "i10-index": i10_index_all,
                }

            except Exception as e:
                print(f"⚠️ Error attempt {attempt+1} for {profile_url}: {e}")
                time.sleep(SLEEP_BETWEEN_CALLS)

        print(f"❌ Failed to fetch data for {profile_url}")
        return None

    except Exception as e:
        print(f"❌ Fatal error in fetch_scholar_data: {e}")
        return None


# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route("/")
def home():
    """Home page: load all faculty names for the dropdowns."""
    try:
        df = load_faculty_df()
        faculty_names = (
            df["Name of Faculty"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .sort_values(key=lambda s: s.str.lower())
            .tolist()
        )
    except Exception as e:
        print("Error loading faculty names:", e)
        faculty_names = []

    return render_template("index.html", faculty_names=faculty_names)


# ---------- View one faculty ----------
@app.route("/fetch_one", methods=["POST"])
def fetch_one():
    """Search and show data for one faculty by name (from dropdown/input)."""
    faculty_name = request.form.get("faculty_name", "").strip()

    if not faculty_name:
        return render_template("result_one.html", error="Please select a faculty name.")

    try:
        df = load_faculty_df()
    except Exception as e:
        return render_template("result_one.html", error=str(e))

    mask = df["Name of Faculty"].astype(str).str.lower() == faculty_name.lower()
    matches = df[mask]

    if matches.empty:
        return render_template(
            "result_one.html",
            error=f"No faculty found with name '{faculty_name}'."
        )

    row = matches.iloc[0]
    url = str(row["Google Scholar Profile URL"]).strip()

    data = fetch_scholar_data(url)
    if not data:
        return render_template("result_one.html", error="Failed to fetch data from Google Scholar.")

    # Update row in Excel
    df.loc[mask, "Citations"] = data["Citations"]
    df.loc[mask, "h-index"] = data["H-index"]
    df.loc[mask, "i10-index"] = data["i10-index"]
    try:
        save_faculty_df(df)
    except PermissionError:
        print("⚠️ Could not save Excel (maybe open in Excel). Skipping save.")

    return render_template("result_one.html", data=data, faculty_name=faculty_name, url=url)


# ---------- Add faculty ----------
@app.route("/add_faculty", methods=["POST"])
def add_faculty():
    """Admin-only: add a new faculty (name + Scholar URL)."""
    admin_password = request.form.get("admin_password", "")
    faculty_name = request.form.get("new_name", "").strip()
    faculty_url = request.form.get("new_url", "").strip()

    if admin_password != ADMIN_PASSWORD:
        return render_template("result_one.html", error="Invalid admin password.")

    if not faculty_name or not faculty_url:
        return render_template("result_one.html", error="Name and URL are required to add faculty.")

    if "scholar.google" not in faculty_url or "user=" not in faculty_url:
        return render_template("result_one.html", error="Please enter a valid Google Scholar Profile URL.")

    try:
        df = load_faculty_df()
    except Exception as e:
        return render_template("result_one.html", error=str(e))

    new_row = {
        "Sr.No": len(df) + 1,
        "Name of Faculty": faculty_name,
        "Google Scholar Profile URL": faculty_url,
        "Citations": None,
        "h-index": None,
        "i10-index": None,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    try:
        save_faculty_df(df)
    except PermissionError:
        print("⚠️ Could not save Excel (maybe open in Excel). Skipping save.")

    msg = f"Faculty '{faculty_name}' added successfully."
    return render_template("result_one.html", message=msg)


# ---------- NEW: Delete faculty ----------
@app.route("/delete_faculty", methods=["POST"])
def delete_faculty():
    """Admin-only: delete a faculty by name."""
    admin_password = request.form.get("admin_password_del", "")
    faculty_name = request.form.get("delete_name", "").strip()

    if admin_password != ADMIN_PASSWORD:
        return render_template("result_one.html", error="Invalid admin password.")

    if not faculty_name:
        return render_template("result_one.html", error="Please select a faculty to delete.")

    try:
        df = load_faculty_df()
    except Exception as e:
        return render_template("result_one.html", error=str(e))

    mask_keep = df["Name of Faculty"].astype(str).str.lower() != faculty_name.lower()
    new_df = df[mask_keep].copy()

    if len(new_df) == len(df):
        return render_template("result_one.html", error=f"No faculty found with name '{faculty_name}'.")

    # Re-number Sr.No
    if "Sr.No" in new_df.columns:
        new_df["Sr.No"] = range(1, len(new_df) + 1)

    try:
        save_faculty_df(new_df)
    except PermissionError:
        print("⚠️ Could not save Excel when deleting (maybe open).")

    msg = f"Faculty '{faculty_name}' deleted successfully."
    return render_template("result_one.html", message=msg)


# ---------- Update Excel for ALL faculty ----------
@app.route("/update_excel", methods=["POST"])
def update_excel():
    """Fetch fresh metrics for all faculty and write updated Excel."""
    try:
        df = load_faculty_df()
    except Exception as e:
        return render_template("result_all.html", error=str(e))

    updated_count = 0
    failed_list = []

    for idx, row in df.iterrows():
        name = str(row["Name of Faculty"])
        url = str(row["Google Scholar Profile URL"]).strip()

        if not url or not url.startswith("http"):
            failed_list.append(name)
            continue

        print(f"🔄 Updating: {name}")
        data = fetch_scholar_data(url)
        if data:
            df.at[idx, "Citations"] = data["Citations"]
            df.at[idx, "h-index"] = data["H-index"]
            df.at[idx, "i10-index"] = data["i10-index"]
            updated_count += 1
        else:
            failed_list.append(name)

        time.sleep(SLEEP_BETWEEN_CALLS)  # respect API rate limits

    # Save updated Excel
    try:
        save_faculty_df(df, UPDATED_PATH)
    except PermissionError:
        print("⚠️ Could not save UPDATED Excel (maybe open).")

    return render_template(
        "result_all.html",
        updated=updated_count,
        total=len(df),
        failed_list=failed_list,
        download_ready=os.path.exists(UPDATED_PATH)
    )


@app.route("/download_updated")
def download_updated():
    """Download the updated Excel file."""
    if not os.path.exists(UPDATED_PATH):
        return "Updated Excel file not found. Please run update first.", 404

    return send_file(UPDATED_PATH, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
