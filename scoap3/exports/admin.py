import csv
import datetime

from django.contrib import admin
from django.http import StreamingHttpResponse

from scoap3.exports.models import AffiliationExportModel, AuthorExportModel
from scoap3.utils.tools import affiliation_export, author_export


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class AffiliationExportModelAdmin(admin.ModelAdmin):
    add_form_template = "admin/exports_form.html"

    def response_add(self, request, obj, post_url_continue=None):
        year = request.POST.get("year", None)
        country = request.POST.get("country_code", None)
        result = affiliation_export(year or None, country or None)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        return StreamingHttpResponse(
            (writer.writerow(row) for row in [result["header"]] + result["data"]),
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scoap3_export_affiliations_{datetime.datetime.now()}.csv"
            },
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = {"title": "Export Affiliations"}
        return super().add_view(request, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        pass

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):  # Here
        return False


class AuthorExportModelAdmin(admin.ModelAdmin):
    add_form_template = "admin/exports_form.html"

    def response_add(self, request, obj, post_url_continue=None):
        year = request.POST.get("year", None)
        country = request.POST.get("country_code", None)
        result = author_export(year or None, country or None)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        return StreamingHttpResponse(
            (writer.writerow(row) for row in [result["header"]] + result["data"]),
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scoap3_export_authors_{datetime.datetime.now()}.csv"
            },
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = {"title": "Export Authors"}
        return super().add_view(request, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        pass

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False


admin.site.register(AffiliationExportModel, AffiliationExportModelAdmin)
admin.site.register(AuthorExportModel, AuthorExportModelAdmin)
