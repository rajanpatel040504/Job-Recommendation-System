from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import UserProfile , Company , Recommendation
from django.contrib.auth.forms import UserCreationForm
from jobs.mlmodel import recommend_jobs
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.db import connection
import pandas as pd
from django.contrib.sessions.models import Session

def welcome(request):
    return render(request, 'welcome.html')

def choice(request):
    return render(request, 'choice.html')

def user_logout(request):
    return render(request, 'welcome.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        email = request.POST.get("email")
        experience = request.POST.get("experience")
        designation = request.POST.get("designation")
        skills = request.POST.get("skills")

        # Check if username already exists
        if UserProfile.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "username_exists"})

        # Create new user
        user = UserProfile.objects.create(
            username=username,
            password=make_password(password),  # Hashing the password
            first_name=name,  # Store full name in first_name
            email=email,
            experience=experience,
            designation=designation,
            skills=skills,
        )
        
        login(request, user)  # Log the user in after signup
        return redirect("view-profile", username=user.username)  # Redirect to profile page

    return render(request, "signup.html")

def user_login(request):
    error = None  # Initialize an error message
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("view-profile", username=user.username)
        else:
            # Check if the username exists to provide a proper error message
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                error = "incorrect_password"
            else:
                error = "username_not_found"

    return render(request, "login.html", {"error": error})

@login_required
def view_profile(request, username):
    user_details = get_object_or_404(UserProfile, username=username)  # Fetch user details
    
    context = {
        'username': user_details.username,
        'name': user_details.first_name + " " + user_details.last_name,  # Get full name
        'email': user_details.email,
        'experience': user_details.experience,
        'designation': user_details.designation,
        'skills': user_details.skills,
    }
    return render(request, 'viewprofile.html', context)

@login_required
def recommend_jobs_view(request):
    username = request.user.username  # Get the logged-in user's username
    
    skills = request.GET.get("skills", "").strip()
    designation = request.GET.get("designation", "").strip()
    experience_str = request.GET.get("experience", "0").strip()

    # Convert experience to integer safely
    try:
        experience = int(experience_str) if experience_str.isdigit() else 0
    except ValueError:
        experience = 0

    recommendations = recommend_jobs(skills, designation, experience)  
    # print(f"Recommendations received: {recommendations}")

    for job in recommendations:
        job["job_id"] = job.pop("job id", None)
        job["company_id"] = job.pop("company id", None)
        job["Job_Title"] = job.pop("Job Title", None)
        job["Job_Salary"] = job.pop("Job Salary", None)
        job["Job_Experience"] = job.pop("Job Experience", None)
        job["Key_Skills"] = job.pop("Key Skills", None)
        

    with connection.cursor() as cur:
        # Get user ID from database
        cur.execute("SELECT id FROM jobs_userprofile WHERE username = %s", [username])
        user_id_row = cur.fetchone()  

        user_id = user_id_row[0] if user_id_row else None  
        
        if recommendations and user_id:
            for job in recommendations:
                company_id = job.get("company id")
                job_id = int(job.get("job id", 0))  
                

                if company_id:
                    try:
                        cur.execute("SELECT company, domain FROM companies WHERE company_id = %s", [company_id])
                        company_info = cur.fetchone()
                        
                        if company_info:
                            job["Company"] = company_info[0]
                            job["Domain"] = company_info[1]
                    except Exception as e:
                        print(f"Database query failed due to: {e}")

                if user_id and company_id:
                    cur.execute("""
                        SELECT id FROM public.jobs_recommendation 
                        WHERE user_id = %s AND job_id = %s AND company_id = %s
                    """, [user_id, job_id, company_id])
                    
                    existing_rec = cur.fetchone()
                    

                    if not existing_rec:  # Insert only if no existing record
                        try:
                           
                            cur.execute("""
                                INSERT INTO public.jobs_recommendation (user_id, job_id, company_id)
                                VALUES (%s, %s, %s)
                            """, [user_id, job_id, company_id])
                            
                            connection.commit()
                        except Exception as e:
                            print(f"❌ Failed to insert recommendation due to: {e}")
                            connection.rollback()

    if not recommendations:
        recommendations = [{"message": "No recommendations found!"}]

    return render(request, "recommendations.html", {"recommendations": recommendations, "username": username})

def recruiter_login(request):
    if request.method == "POST":
        company_id = request.POST["companyid"]
        password = request.POST["companypassword"]
       
        company = Company.objects.filter(company_id=company_id, company_pwd=password).first()
        if company:
            request.session["company_id"] = company.company_id
            return redirect("dashboard")

    return render(request, "recruiter_login.html")

@login_required
def dashboard(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("recruiter_login")

    company = Company.objects.get(company_id=company_id)
    return render(request, "dashboard.html", {"company": company})


@login_required
def job_postings(request):
    company = request.session.get('company')
    company_id = request.session.get('company_id')  

    if not company_id:
        return redirect('recruiter_login')  

    # Read the CSV file
    df = pd.read_csv('jobs_info.csv')
    
    filtered_jobs = df[df['company id'] == int(company_id)]
    jobs_list = filtered_jobs.to_dict('records')
    
    for job in jobs_list:
        job["job_id"] = job.pop("job id", None)
        job["job_title"] = job.pop("Job Title", None)
        job["job_experience"] = job.pop("Job Experience", None)
        job["key_skills"] = job.pop("Key Skills",None)

    return render(request, 'job_postings.html', {'jobs': jobs_list, 'company': company})

@login_required
def candidates(request):
    company_id = request.session.get('company_id')  # Get company_id from session

    if not company_id:
        return redirect('recruiter_login')  # Redirect if not logged in

    candidates_info = []

    with connection.cursor() as cur:
        try:
            cur.execute("""
                SELECT u.id, u.name, u.email, u.experience, u.designation, u.skills, r.job_id
                FROM recommendations r
                JOIN userinfo u ON r.user_id = u.id
                WHERE r.company_id = %s;
            """, [company_id])
            candidates_info = cur.fetchall()
        except Exception as e:
            print(f"Error fetching candidates: {e}")
            return render(request, 'candidates.html', {'error': "Failed to fetch candidates."})

    return render(request, 'candidates.html', {'candidates_info': candidates_info})
        