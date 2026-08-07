from django.contrib import admin
from django.core.mail import send_mail
from .models import Entry, EntryProposal


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')


@admin.register(EntryProposal)
class EntryProposalAdmin(admin.ModelAdmin):
    list_display = ('proposed_title', 'entry', 'proposer_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('proposed_title', 'proposer_name')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status == 'approved':
            if obj.entry:
                # Update existing entry
                obj.entry.title = obj.proposed_title
                obj.entry.content = obj.proposed_content
                obj.entry.save()
            else:
                # Create new entry
                entry, created = Entry.objects.get_or_create(
                    title=obj.proposed_title,
                    defaults={'content': obj.proposed_content}
                )
                if not created:
                    entry.content = obj.proposed_content
                    entry.save()
                obj.entry = entry
                obj.save()

            # Email the proposer if they provided an address
            if obj.proposer_email:
                send_mail(
                    subject=f'Your proposal "{obj.proposed_title}" has been approved',
                    message=(
                        f'Hi {obj.proposer_name or "there"},\n\n'
                        f'Your proposed entry "{obj.proposed_title}" has been approved and is now live.\n\n'
                        f'Thank you for your contribution!'
                    ),
                    from_email=None,
                    recipient_list=[obj.proposer_email],
                    fail_silently=True,
                )

        elif obj.status == 'rejected':
            if obj.proposer_email and obj.send_rejection_email:
                send_mail(
                    subject=f'Your proposal "{obj.proposed_title}" was not approved',
                    message=(
                        f'Hi {obj.proposer_name or "there"},\n\n'
                        f'Thank you for submitting "{obj.proposed_title}". '
                        f'Unfortunately your proposal was not approved at this time.\n\n'
                        f'{("Reason: " + obj.admin_notes) if obj.admin_notes else ""}'
                    ),
                    from_email=None,
                    recipient_list=[obj.proposer_email],
                    fail_silently=True,
                )