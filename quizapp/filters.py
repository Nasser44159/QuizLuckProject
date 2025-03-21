from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

class ExamFilter(SimpleListFilter):
    title = _("By exam")
    parameter_name = "exam"

    def lookups(self, request, model_admin):
        exams = set(comment.unique_id.split('_')[0] for comment in model_admin.model.objects.all() if comment.unique_id)
        return [(exam, exam) for exam in sorted(exams)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(unique_id__startswith=self.value())
        return queryset
