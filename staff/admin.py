from django.contrib import admin


from .models import Staff,LeaveRequest,FeedBackStaff,NotificationStaffs

admin.site.register(Staff)
admin.site.register(NotificationStaffs)
<<<<<<< HEAD
=======

>>>>>>> bd0dc2661a40dec183d115edf39bb71d9b09c58e



@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'message', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'message')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status=1)  # 1 = Approved
        self.message_user(request, f"{queryset.count()} leave requests have been approved.")
    approve_requests.short_description = "Approve selected leave requests"

    def reject_requests(self, request, queryset):
        queryset.update(status=2)  # 2 = Rejected
        self.message_user(request, f"{queryset.count()} leave requests have been rejected.")
    reject_requests.short_description = "Reject selected leave requests"
# Register your models here.



@admin.register(FeedBackStaff)
class FeedBackStaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'feedback', 'feedback_reply', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('staff_id__full_name', 'feedback')  # Searching by student's full name and feedback content
    actions = ['mark_feedback_replied', 'delete_feedbacks']

    # Action to mark feedback as replied
    def mark_feedback_replied(self, request, queryset):
        queryset.update(feedback_reply="Replied")  # You can customize this action as needed
        self.message_user(request, f"{queryset.count()} feedbacks have been marked as replied.")
    mark_feedback_replied.short_description = "Mark selected feedbacks as replied"

    # Action to delete selected feedbacks
    def delete_feedbacks(self, request, queryset):
        queryset.delete()
        self.message_user(request, f"{queryset.count()} feedbacks have been deleted.")
    delete_feedbacks.short_description = "Delete selected feedbacks"