import csv
from datetime import datetime

from django.contrib import messages

# from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.edit import FormView

from scoap3.exports.forms import AffiliationExportForm, AuthorExportForm, YearExportForm
from scoap3.utils.tools import affiliation_export, author_export, year_export


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


class ExportView(FormView):
    template_name = "admin/tools.html"
    form_class = AffiliationExportForm
    second_form_class = AuthorExportForm
    third_form_class = YearExportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form2" not in context:
            context["form2"] = self.second_form_class()
        if "form3" not in context:
            context["form3"] = self.third_form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form2 = self.second_form_class(request.POST)
        form3 = self.third_form_class(request.POST)
        if form.is_valid() or form2.is_valid() or form3.is_valid():
            return self.form_valid(form, form2, form3)
        else:
            return self.form_invalid(form, form2, form3)

    def form_valid(self, form, form2, form3):
        try:
            if "affiliation_export" in self.request.POST:
                action_name = "affiliation_export"
                year = form.cleaned_data.get("aff_year")
                country = form.cleaned_data.get("aff_country").code
                result = affiliation_export(year or None, country or None)

            elif "author_export" in self.request.POST:
                action_name = "author_export"
                year = form2.cleaned_data.get("author_year")
                country = form2.cleaned_data.get("author_country").code
                result = author_export(year or None, country or None)

            elif "year_export" in self.request.POST:
                action_name = "year_export"
                start_date = form3.cleaned_data.get("start_date")
                end_date = form3.cleaned_data.get("end_date")
                pub = form3.cleaned_data.get("publisher_name") or None
                start_date_string = (
                    start_date.strftime("%Y-%m-%d") if start_date else None
                )
                end_date_string = end_date.strftime("%Y-%m-%d") if end_date else None
                result = year_export(start_date_string, end_date_string, pub)

            response = generate_csv_response(result, action_name)
            return response

        except Exception as ex:
            messages.error(self.request, f"There was an error: {ex}")
            return self.form_invalid(form, form2, form3)

    def form_invalid(self, form, form2, form3):
        return self.render_to_response(
            self.get_context_data(form=form, form2=form2, form3=form3)
        )
