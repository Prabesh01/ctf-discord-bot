from django.contrib import admin
from .models import Challenge, Solve, Category


class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name",)


class ChallengeAdmin(admin.ModelAdmin):
  list_display = ("title", "is_over", "disable_solve_notif", "solve_count")
  # exclude = ('message_id',)


class SolveAdmin(admin.ModelAdmin):

    list_display = [field.name for field in Solve._meta.get_fields() if field.name != 'id']

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False  


admin.site.register(Category,CategoryAdmin)
admin.site.register(Challenge,ChallengeAdmin)
admin.site.register(Solve,SolveAdmin)