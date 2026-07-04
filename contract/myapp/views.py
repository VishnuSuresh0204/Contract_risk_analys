from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Avg
import json
import os

from .models import *
from .engine import (
    extract_text_from_file,
    detect_clauses,
    calculate_risk,
    get_missing_clauses,
    generate_report_file,
    get_chatbot_response
)

# -------------------------------------------------
# LOGIN CHECK
# -------------------------------------------------

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

def admin_home(request):

    check = require_login(request)
    if check:
        return check

    context = {
        "users": UserProfile.objects.count(),
        "contracts": Contract.objects.count(),
        "analyzed": Contract.objects.filter(status="analyzed").count(),
        "high_risk": RiskReport.objects.filter(overall_risk_level="high").count(),
    }

    return render(
        request,
        "ADMIN/admin_home.html",
        context
    )

def admin_view_users(request):

    check = require_login(request)
    if check:
        return check

    users = UserProfile.objects.all()

    return render(
        request,
        "ADMIN/view_users.html",
        {"val": users}
    )

def admin_view_contracts(request):

    check = require_login(request)
    if check:
        return check

    contracts = Contract.objects.all().order_by("-uploaded_date")

    return render(
        request,
        "ADMIN/view_contracts.html",
        {"val": contracts}
    )

def admin_view_contract_detail(request):

    check = require_login(request)
    if check:
        return check

    contract_id = request.GET.get("id")

    contract = get_object_or_404(
        Contract,
        id=contract_id
    )

    clauses = contract.clauses.all()
    missing = contract.missing_clauses.all()
    report = RiskReport.objects.filter(contract=contract).first()

    return render(
        request,
        "ADMIN/contract_detail.html",
        {
            "contract": contract,
            "clauses": clauses,
            "missing": missing,
            "report": report
        }
    )

def admin_manage_rules(request):

    check = require_login(request)
    if check:
        return check

    if request.method == "POST":

        raw_clause_type = (request.POST.get("clause_type") or "").strip()

        if not raw_clause_type:
            messages.error(request, "Clause type name is required")
            return redirect("/admin_manage_rules")

        # If a clause type with the same name already exists (regardless
        # of case), reuse its exact casing so "Payment Terms" and
        # "payment terms" don't end up treated as two different clauses.
        existing = ClauseRule.objects.filter(
            clause_type__iexact=raw_clause_type
        ).first()

        clause_type = existing.clause_type if existing else raw_clause_type

        ClauseRule.objects.create(
            clause_type=clause_type,
            keyword=request.POST.get("keyword"),
            risk_level_if_missing=request.POST.get("risk_level_if_missing"),
            description=request.POST.get("description")
        )

        messages.success(request, "Rule added successfully")

        return redirect("/admin_manage_rules")

    rules = ClauseRule.objects.all().order_by("clause_type")

    # Distinct existing clause type names, handy for the template to
    # power an autocomplete/datalist so the admin can reuse a name
    # rather than retyping it.
    existing_types = (
        ClauseRule.objects
        .values_list("clause_type", flat=True)
        .distinct()
        .order_by("clause_type")
    )

    return render(
        request,
        "ADMIN/manage_rules.html",
        {
            "val": rules,
            "existing_types": existing_types
        }
    )

def admin_toggle_rule(request):

    rule_id = request.GET.get("id")

    rule = get_object_or_404(
        ClauseRule,
        id=rule_id
    )

    rule.is_active = not rule.is_active
    rule.save()

    return redirect("/admin_manage_rules")

def admin_send_notification(request):

    check = require_login(request)
    if check:
        return check

    if request.method == "POST":

        Notification.objects.create(
            title=request.POST.get("title"),
            message=request.POST.get("message"),
            target_role=request.POST.get("target_role")
        )

        messages.success(request, "Notification sent")

        return redirect("/admin_send_notification")

    return render(
        request,
        "ADMIN/send_notification.html"
    )

def admin_view_feedback(request):

    check = require_login(request)
    if check:
        return check

    feedback = Feedback.objects.all().order_by("-created_at")

    avg_rating = feedback.aggregate(Avg("rating"))["rating__avg"]

    return render(
        request,
        "ADMIN/view_feedback.html",
        {
            "val": feedback,
            "avg_rating": avg_rating
        }
    )

def admin_view_complaints(request):

    check = require_login(request)
    if check:
        return check

    complaints = Complaint.objects.all().order_by("-created_at")

    return render(
        request,
        "ADMIN/view_complaints.html",
        {"complaints": complaints}
    )

def admin_reply_complaint(request):

    check = require_login(request)
    if check:
        return check

    if request.method == "POST":

        complaint_id = request.POST.get("complaint_id")
        reply_text = request.POST.get("reply")

        complaint = get_object_or_404(
            Complaint,
            id=complaint_id
        )

        complaint.reply = reply_text
        complaint.status = "resolved"
        complaint.save()

        messages.success(request, "Reply submitted successfully")

    return redirect("/admin_view_complaints")

# -------------------------------------------------
# USER
# -------------------------------------------------

def user_home(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    contracts = Contract.objects.filter(
        user=user
    ).order_by("-uploaded_date")[:5]

    context = {
        "total_contracts": Contract.objects.filter(user=user).count(),
        "high_risk": RiskReport.objects.filter(
            contract__user=user,
            overall_risk_level="high"
        ).count(),
        "recent": contracts
    }

    return render(
        request,
        "USER/user_home.html",
        context
    )

def user_upload_contract(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    if request.method == "POST":

        uploaded_file = request.FILES.get("contract_file")
        file_ext = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")

        contract = Contract.objects.create(
            user=user,
            title=request.POST.get("title") or uploaded_file.name,
            original_file=uploaded_file,
            file_type=file_ext,
            status="uploaded"
        )

        messages.success(request, "Contract uploaded successfully")

        return redirect(f"/user_analyze_contract?id={contract.id}")

    return render(
        request,
        "USER/upload_contract.html"
    )

def user_analyze_contract(request):

    check = require_login(request)
    if check:
        return check

    contract_id = request.GET.get("id")

    contract = get_object_or_404(
        Contract,
        id=contract_id
    )

    contract.status = "processing"
    contract.save()

    # ---- Step 1: Text extraction ----
    text, page_count = extract_text_from_file(
        contract.original_file.path,
        contract.file_type
    )

    contract.extracted_text = text
    contract.page_count = page_count

    # ---- Step 2: Clause detection (NLP + rule matching) ----
    detected_clauses = detect_clauses(text)

    ContractClause.objects.filter(contract=contract).delete()

    for clause_data in detected_clauses:
        ContractClause.objects.create(
            contract=contract,
            clause_type=clause_data["clause_type"],
            is_present=clause_data["is_present"],
            clause_text=clause_data["clause_text"],
            risk_level=clause_data["risk_level"],
            risk_reason=clause_data["risk_reason"],
            recommendation=clause_data["recommendation"]
        )

    # ---- Step 3: Missing clause identification ----
    missing = get_missing_clauses(detected_clauses)

    MissingClause.objects.filter(contract=contract).delete()

    for missing_data in missing:
        MissingClause.objects.create(
            contract=contract,
            clause_type=missing_data["clause_type"],
            risk_level=missing_data["risk_level"],
            recommendation=missing_data["recommendation"]
        )

    # ---- Step 4: Rule-based overall risk scoring ----
    risk_score, risk_level, summary = calculate_risk(
        detected_clauses,
        missing
    )

    RiskReport.objects.filter(contract=contract).delete()

    report = RiskReport.objects.create(
        contract=contract,
        overall_risk_score=risk_score,
        overall_risk_level=risk_level,
        total_clauses_detected=len([c for c in detected_clauses if c["is_present"]]),
        missing_clauses_count=len(missing),
        summary=summary
    )

    # ---- Step 5: Generate downloadable report file ----
    report_path = generate_report_file(contract, report)
    report.report_file = report_path
    report.save()

    contract.status = "analyzed"
    contract.save()

    messages.success(request, "Contract analysis completed")

    return redirect(f"/user_contract_detail?id={contract.id}")

def user_view_contracts(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    contracts = Contract.objects.filter(
        user=user
    ).order_by("-uploaded_date")

    return render(
        request,
        "USER/view_contracts.html",
        {"val": contracts}
    )

def user_contract_detail(request):

    check = require_login(request)
    if check:
        return check

    contract_id = request.GET.get("id")

    contract = get_object_or_404(
        Contract,
        id=contract_id
    )

    clauses = contract.clauses.all()
    missing = contract.missing_clauses.all()
    report = RiskReport.objects.filter(contract=contract).first()

    return render(
        request,
        "USER/contract_detail.html",
        {
            "contract": contract,
            "clauses": clauses,
            "missing": missing,
            "report": report
        }
    )

def user_download_report(request):

    check = require_login(request)
    if check:
        return check

    contract_id = request.GET.get("id")

    report = get_object_or_404(
        RiskReport,
        contract_id=contract_id
    )

    return redirect(report.report_file.url)

# -------------------------------------------------
# OFFLINE AI CHATBOT
# -------------------------------------------------

def user_chatbot(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    contract_id = request.GET.get("contract_id")

    conversation = ChatConversation.objects.filter(
        user=user,
        contract_id=contract_id
    ).first()

    if not conversation:
        conversation = ChatConversation.objects.create(
            user=user,
            contract_id=contract_id,
            title="Contract Q&A"
        )

    chat_messages = conversation.messages.all().order_by("created_at")

    return render(
        request,
        "USER/chatbot.html",
        {
            "conversation": conversation,
            "val": chat_messages
        }
    )

def user_send_chat_message(request):

    check = require_login(request)
    if check:
        return check

    if request.method == "POST":

        conversation_id = request.POST.get("conversation_id")
        user_message = request.POST.get("message")

        conversation = get_object_or_404(
            ChatConversation,
            id=conversation_id
        )

        ChatMessage.objects.create(
            conversation=conversation,
            sender_type="user",
            message=user_message
        )

        # ---- Offline AI assistant generates a contextual reply ----
        contract = conversation.contract

        bot_reply = get_chatbot_response(
            user_message=user_message,
            contract=contract
        )

        ChatMessage.objects.create(
            conversation=conversation,
            sender_type="bot",
            message=bot_reply
        )

        return redirect(f"/user_chatbot?contract_id={contract.id if contract else ''}")

    return redirect("/user_home")

# -------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------

def user_notifications(request):

    check = require_login(request)
    if check:
        return check

    notifications = Notification.objects.filter(
        target_role__in=["user", "all"]
    ).order_by("-created_at")

    return render(
        request,
        "USER/notifications.html",
        {"val": notifications}
    )

# -------------------------------------------------
# FEEDBACK
# -------------------------------------------------

def user_feedback(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    if request.method == "POST":

        Feedback.objects.create(
            user=user,
            rating=request.POST.get("rating"),
            message=request.POST.get("message")
        )

        messages.success(request, "Thank you for your feedback")

        return redirect("/user_home")

    return render(
        request,
        "USER/feedback.html"
    )

# -------------------------------------------------
# COMPLAINTS
# -------------------------------------------------

def user_complaints(request):

    check = require_login(request)
    if check:
        return check

    user = UserProfile.objects.get(
        loginid_id=request.session["lid"]
    )

    if request.method == "POST":

        subject = request.POST.get("subject")
        message = request.POST.get("message")

        Complaint.objects.create(
            user=user,
            subject=subject,
            message=message
        )

        messages.success(request, "Complaint submitted successfully")

        return redirect("/user_complaints")

    complaints = Complaint.objects.filter(
        user=user
    ).order_by("-created_at")

    return render(
        request,
        "USER/complaints.html",
        {"complaints": complaints}
    )