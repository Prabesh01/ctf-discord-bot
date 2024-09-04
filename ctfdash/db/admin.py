from django.contrib import admin
from .models import Challenge, Solve, Category, Setting
from django.contrib.auth.models import User, Group
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(username=request.user.username)

    def has_add_permission(self, request):
        if request.user.is_superuser: return True        
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            for field_name, field in form.base_fields.items():
                if field_name not in ['password']:
                    field.widget = forms.HiddenInput()
                    field.required = False
        return form
    
    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            for field in form.changed_data:
                if field not in ['password']:
                    raise ValidationError('You are not allowed to change these fields')                 
            # if form.cleaned_data['password'] and form.cleaned_data['password'] != obj.password:
            #     obj.set_password(form.cleaned_data['password'])

        return super().save_model(request, obj, form, change)    

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser: return False


class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


class SettingAdmin(admin.ModelAdmin):
    list_display = ("new_challenge_announce_message", "top_x_priority", 'display_solves_upto', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return False


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser: return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return False
        return True


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "is_over", "disable_solve_notif", "solve_count")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):        
        obj.user = request.user
        setting, _ = Setting.objects.get_or_create(user=obj.user)
        if not setting.challenge_webhook or not setting.solve_webhook:
            self.message_user(request, 'Cannot add/edit challenge because challenge_webhook and solve_webhook are not set in Settings.', level='error')
            return False
        super().save_model(request, obj, form, change)


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            form.base_fields['category'].queryset = Category.objects.filter(user=request.user)
        return form

    def has_add_permission(self, request):
        if request.user.is_superuser: return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return False
        return True


class SolveAdmin(admin.ModelAdmin):

    list_display = [field.name for field in Solve._meta.get_fields() if field.name != 'id']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(challenge__user=request.user)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Setting, SettingAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Challenge,ChallengeAdmin)
admin.site.register(Solve,SolveAdmin)