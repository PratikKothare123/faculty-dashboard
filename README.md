# 📚 Google Scholar Faculty Dashboard

A Flask-based web application that automatically fetches and manages faculty research metrics from Google Scholar using SerpAPI.

This project helps educational institutions maintain updated research performance data such as citations, h-index, and i10-index in an automated and structured manner.

---

## 🌐 Live Deployment

🔗 **Live Website:**  
https://faculty-dashboard-ygz6.onrender.com

---

## ✨ Highlights

- 🔍 Fetch research metrics for individual faculty members
- 📊 Bulk update research data for all faculty
- 📁 Automatically update Excel database
- ➕ Add new faculty records
- ❌ Delete faculty records
- 🔐 Admin password protection
- ☁️ Cloud deployment using Render
- 🔒 Secure API key handling using environment variables
- 📥 Download updated Excel reports

---

## 🛠 Tech Stack

### Backend
- Python
- Flask
- Pandas
- OpenPyXL

### API Integration
- SerpAPI (Google Scholar Author Engine)

### Frontend
- HTML
- CSS

### Deployment & Security
- Gunicorn (Production Server)
- Render (Cloud Hosting)
- Environment Variables (.env)

---

## 📂 Project Structure
```
faculty-dashboard/
│
├── app.py 
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
│
├── data/
│ ├── faculty_data.xlsx
│ └── faculty_data_updated.xlsx
│
├── static/
│ ├── style.css
│ └── logo.png
│
└── templates/
├── index.html
├── result_one.html 
└── result_all.html 
```
---

## 💻 How to Clone and Run This Project on Another Machine

### Step 1️⃣ Clone Repository

```bash
git clone https://github.com/PratikKothare123/faculty-dashboard.git
cd faculty-dashboard
```
### Step 2️⃣ Create Virtual Environment
`
python -m venv venv
`
Activate Virtual Environment:

#### Windows
``venv\Scripts\activate``
#### Mac/Linux
```source venv/bin/activate```
### Step 3️⃣ Install Dependencies
```pip install -r requirements.txt```
### Step 4️⃣ Create ```.env``` File
Create a file named``` .env ```in the root folder and add:

```SERPAPI_KEY=your_serpapi_key_here```
### Step 5️⃣ Run Application
```python app.py```
Open browser and visit:

```http://127.0.0.1:5000```
## 📥 How to Use the Application
- Select a faculty name to fetch research metrics

- Update all faculty records using bulk update

- Download updated Excel report

- Admin can add or delete faculty records

## 🔐 Security Implementation
- API keys are stored using environment variables

- Admin operations require password authentication

- .env file is ignored using .gitignore

## 🔮 Future Enhancements
- Role-based multiple admin access

- Authentication and user login system

- Advanced research analytics dashboard

- Graph and trend visualization

- Database integration for scalability

- Scheduled automatic updates
---
## 👨‍💻 Developed By
Pratik Kothare

Computer Science Student

## GitHub: https://github.com/PratikKothare123
---
### ⭐ If you like this project, don’t forget to star the repository!
