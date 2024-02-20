import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.edit import FormView

from scoap3.exports.forms import AffiliationExportForm, AuthorExportForm
from scoap3.utils.tools import affiliation_export, author_export


def generate_csv_response(data, action_name, write_header=True):
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="scoap3_{action_name}_{datetime.now()}.csv"'  # noqa
        },
    )

    writer = csv.writer(response)
    if write_header:
        writer.writerow(data.get("header"))
    for row in data.get("data", []):
        writer.writerow(row)

    return response


class ExportView(PermissionRequiredMixin, FormView):
    permission_required = "users.partner_export"
    template_name = "tools/export.html"
    form_class = AffiliationExportForm
    second_form_class = AuthorExportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form2" not in context:
            context["form2"] = self.second_form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            return self.form_valid(form, form2)
        else:
            return self.form_invalid(form, form2)

    def form_valid(self, form, form2):
        try:
            if "affiliation_export" in self.request.POST:
                action_name = "affiliation_export"
                year = form.cleaned_data.get("year")
                country = form.cleaned_data.get("country_code")
                result = affiliation_export(year or None, country or None)
            if "author_export" in self.request.POST:
                action_name = "author_export"
                year = form2.cleaned_data.get("year")
                country = form2.cleaned_data.get("country_code")
                result = author_export(year or None, country or None)

            response = generate_csv_response(result, action_name)

            return response
        except Exception as ex:
            messages.error(self.request, f"There was an error: {ex}")
            return self.form_invalid(form, form2)

    def form_invalid(self, form, form2):
        return self.render_to_response(self.get_context_data(form=form, form2=form2))
