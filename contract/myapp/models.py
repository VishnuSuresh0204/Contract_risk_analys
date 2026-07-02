from django.db import models
from django.contrib.auth.models import AbstractUser
 
 
# ---------------- LOGIN ---------------- #
 
class Login(AbstractUser):
    userType = models.CharField(
        max_length=50
    )
 
    viewPass = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
 
    def __str__(self):
        return self.username
 
 
# ---------------- USER (CLIENT) PROFILE ---------------- #
 
class UserProfile(models.Model):
    loginid = models.ForeignKey(
        Login,
        on_delete=models.CASCADE
    )
 
    name = models.CharField(max_length=200)
 
    email = models.EmailField()
 
    phone = models.CharField(max_length=20)
 
    organization = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
 
    address = models.TextField(
        null=True,
        blank=True
    )
 
    profile_pic = models.ImageField(
        upload_to="user_profiles",
        null=True,
        blank=True
    )
 
    def __str__(self):
        return self.name
    

    
class Contract(models.Model):
 
    FILE_TYPE_CHOICES = (
        ("pdf", "PDF"),
        ("docx", "DOCX"),
        ("txt", "TXT"),
    )
 
    STATUS_CHOICES = (
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("analyzed", "Analyzed"),
        ("failed", "Failed"),
    )
 
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
 
    title = models.CharField(
        max_length=255
    )
 
    original_file = models.FileField(
        upload_to="contracts/"
    )
 
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES
    )
 
    extracted_text = models.TextField(
        null=True,
        blank=True
    )
 
    page_count = models.IntegerField(
        null=True,
        blank=True
    )
 
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="uploaded"
    )
 
    uploaded_date = models.DateTimeField(
        auto_now_add=True
    )
 
    analyzed_date = models.DateTimeField(
        null=True,
        blank=True
    )
 
    def __str__(self):
        return f"{self.title} - {self.user.name}"
    

class ClauseRule(models.Model):
 
    CLAUSE_TYPE_CHOICES = (
        ("confidentiality", "Confidentiality"),
        ("payment_terms", "Payment Terms"),
        ("termination", "Termination Conditions"),
        ("liability", "Liability"),
        ("indemnification", "Indemnification"),
        ("dispute_resolution", "Dispute Resolution"),
        ("force_majeure", "Force Majeure"),
        ("intellectual_property", "Intellectual Property"),
        ("warranty", "Warranty"),
        ("data_privacy", "Data Privacy"),
    )
 
    RISK_LEVEL_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
 
    clause_type = models.CharField(
        max_length=50,
        choices=CLAUSE_TYPE_CHOICES
    )
 
    keyword = models.CharField(
        max_length=200
    )
 
    risk_level_if_missing = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="high"
    )
 
    description = models.TextField(
        null=True,
        blank=True
    )
 
    is_active = models.BooleanField(
        default=True
    )
 
    def __str__(self):
        return f"{self.clause_type} - {self.keyword}"
    


class ContractClause(models.Model):
 
    CLAUSE_TYPE_CHOICES = ClauseRule.CLAUSE_TYPE_CHOICES
 
    RISK_LEVEL_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
 
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="clauses"
    )
 
    clause_type = models.CharField(
        max_length=50,
        choices=CLAUSE_TYPE_CHOICES
    )
 
    is_present = models.BooleanField(
        default=False
    )
 
    clause_text = models.TextField(
        null=True,
        blank=True
    )
 
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="low"
    )
 
    risk_reason = models.TextField(
        null=True,
        blank=True
    )
 
    recommendation = models.TextField(
        null=True,
        blank=True
    )
 
    def __str__(self):
        return f"{self.contract.title} - {self.clause_type}"
 

class RiskReport(models.Model):
 
    RISK_LEVEL_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
 
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="risk_report"
    )
 
    overall_risk_score = models.FloatField(
        default=0
    )
 
    overall_risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="low"
    )
 
    total_clauses_detected = models.IntegerField(
        default=0
    )
 
    missing_clauses_count = models.IntegerField(
        default=0
    )
 
    summary = models.TextField(
        null=True,
        blank=True
    )
 
    report_file = models.FileField(
        upload_to="reports/",
        null=True,
        blank=True
    )
 
    generated_date = models.DateTimeField(
        auto_now_add=True
    )
 
    def __str__(self):
        return f"Report - {self.contract.title}"
    


class MissingClause(models.Model):
 
    RISK_LEVEL_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
 
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="missing_clauses"
    )
 
    clause_type = models.CharField(
        max_length=50,
        choices=ClauseRule.CLAUSE_TYPE_CHOICES
    )
 
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default="high"
    )
 
    recommendation = models.TextField(
        null=True,
        blank=True
    )
 
    def __str__(self):
        return f"{self.contract.title} - Missing {self.clause_type}"
 
 
# ---------------- CHAT CONVERSATION (OFFLINE AI ASSISTANT) ---------------- #
 
class ChatConversation(models.Model):
 
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
 
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
 
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    def __str__(self):
        return f"{self.user.name} - {self.title or self.id}"
 


class ChatMessage(models.Model):
 
    SENDER_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
    )
 
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
 
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES
    )
 
    message = models.TextField()
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    def __str__(self):
        return f"{self.sender_type} - {self.conversation_id}"
 
 
# ---------------- NOTIFICATION ---------------- #
 
class Notification(models.Model):
 
    title = models.CharField(
        max_length=200
    )
 
    message = models.TextField()
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    target_role = models.CharField(
        max_length=50
    )
 
    def __str__(self):
        return self.title
 
 
# ---------------- FEEDBACK ---------------- #
 
class Feedback(models.Model):
 
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
 
    rating = models.IntegerField()
 
    message = models.TextField()
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    def __str__(self):
        return f"{self.user.name} - {self.rating}"
 
 
# ---------------- COMPLAINT ---------------- #
 
class Complaint(models.Model):
 
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
 
    subject = models.CharField(
        max_length=200
    )
 
    message = models.TextField()
 
    reply = models.TextField(
        null=True,
        blank=True
    )
 
    status = models.CharField(
        max_length=30,
        default="pending"
    )
 
    created_at = models.DateTimeField(
        auto_now_add=True
    )
 
    def __str__(self):
        return self.subject