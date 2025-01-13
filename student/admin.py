from django.contrib import admin
from .models import Student,Course
from .models import LeaveRequest

admin.site.register(Student)
admin.site.register(Course)



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
