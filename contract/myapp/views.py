from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *




def require_login(request, redirect_url="/login"):
    if "lid" not in request.session:
        messages.error(request, "Please login first")
        return redirect(redirect_url)
    return None
 
# -------------------------------------------------
# INDEX
# -------------------------------------------------
 
def index(request):
    logout(request)
    return render(request, "index.html")
 
# -------------------------------------------------
# LOGIN
# -------------------------------------------------
 
def login_view(request):
 
    if request.method == "POST":
 
        username = request.POST.get("username")
        password = request.POST.get("password")
 
        user = authenticate(
            username=username,
            password=password
        )
 
        if user:
 
            login(request, user)
            request.session["lid"] = user.id
 
            if user.userType == "admin":
                return redirect("/admin_home")
 
            elif user.userType == "user":
                return redirect("/user_home")
 
        messages.error(request, "Invalid username or password")
        return redirect("/login")
 
    return render(request, "login.html")
 
def signout(request):
    logout(request)
    request.session.flush()
    return redirect("/")
 
# -------------------------------------------------
# USER REGISTRATION
# -------------------------------------------------
 
def register_user(request):
 
    if request.method == "POST":
 
        username = request.POST.get("username")
        password = request.POST.get("password")
 
        if Login.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("/register_user")
 
        login_obj = Login.objects.create_user(
            username=username,
            password=password,
            userType="user",
            viewPass=password
        )
 
        UserProfile.objects.create(
            loginid=login_obj,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            organization=request.POST.get("organization"),
            address=request.POST.get("address")
        )
 
        messages.success(request, "Registration successful")
        return redirect("/login")
 
    return render(request, "user_register.html")
 
# -------------------------------------------------
# ADMIN
# -------------------------------------------------
 
