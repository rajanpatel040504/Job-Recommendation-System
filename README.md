# Job Recommendation System

## Overview
This is a **Job Recommendation System** built using **Django** for the backend and **PostgreSQL** as the database. The system helps recruiters and job seekers by providing job postings and candidate recommendations based on stored data.

---

## Installation & Setup

### **1. Clone the Repository**
```bash
 git clone https://github.com/rajanpatel040504/Job-Recommendation-System/tree/main
 cd job_recommendation_system
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate    # For Windows
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up the Database (PostgreSQL)**
1. Install PostgreSQL and create a database.
2. Update `settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Load Initial Data**
⚠️ **WARNING:** Before running the project, upload company data from `company.txt` to the **company** table.According the table name you can change in views.py file.


---

## Running the Application
```bash
python manage.py runserver
```
Access the project at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Features
### **1. User Authentication**
- Recruiters and candidates can log in and register.

### **2. Job Postings**
- Jobs are stored in `jobs.csv`.
- Jobs are fetched from the database for each company.

### **3. Machine Learning-Based Job Recommendations**
The system uses an **ML model (`jobs1.py`)** to recommend jobs based on:
- **Skills matching**: Using **TF-IDF Vectorization** and **Cosine Similarity**.
- **Job title matching**: Similarity calculation between job titles.
- **Experience similarity**: Adjusted scoring based on job experience range.

#### **How the ML Model Works**
1. **Data Preprocessing**  
   - Loads job information from `jobs_info.csv`.  
   - Extracts experience range from job descriptions.  

2. **Feature Engineering**  
   - Uses `TfidfVectorizer` to process **Key Skills** and **Job Titles**.  
   - Computes **Cosine Similarity** between job postings and candidate profiles.  

3. **Job Recommendation Function (`recommend_jobs()`)**  
   - Takes **skills, job title, and experience** as input.  
   - Computes similarity scores and ranks jobs accordingly.  
   - Filters and returns the top 10 job recommendations.  

### **4. Debugging**
- Debug the application **line by line** in `views.py` to ensure smooth database connections.

---

## Files & Structure
- `requirements.txt`: Contains all necessary Python packages.
- `company.txt`: Contains company data (must be inserted first).
- `jobs.csv`: Stores job posting data.
- `views.py`: Handles logic for job postings and recommendations.
- `templates/`: Contains HTML templates for the frontend.
- `mlmodel.py` : Contains the **Machine Learning model** for job recommendations.

---

## Contributors
- **[Rajan Patel]** - Developer

For any issues or contributions, feel free to open a pull request or raise an issue!

