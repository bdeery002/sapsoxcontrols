from django.db import models

class Entry(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()  # raw markdown
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "entries"


class EntryProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True)
    proposed_title = models.CharField(max_length=200)
    proposed_content = models.TextField()
    proposer_name = models.CharField(max_length=100, blank=True)
    proposer_email = models.EmailField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True)
    send_rejection_email = models.BooleanField(default=False)

    def __str__(self):
        return f"Proposal: {self.proposed_title} ({self.status})"

    class Meta:
        verbose_name_plural = "entry proposals"