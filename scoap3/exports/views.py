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
        if self.request.user.is_superuser and "form3" not in context:
            context["form3"] = self.third_form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form2 = self.second_form_class(request.POST)
        form3 = self.third_form_class(request.POST) if request.user.is_superuser else None

        is_valid = form.is_valid() or form2.is_valid() or (form3 is not None and form3.is_valid())
        if is_valid:
            return self.form_valid(form, form2, form3)
        else:
            return self.form_invalid(form, form2, form3)

    def form_valid(self, form, form2, form3):
        try:
            result = None
            action_name = None

            if "affiliation_export" in self.request.POST:
                action_name = "affiliation_export"
                year = form.cleaned_data.get("aff_year")
                country_field = form.cleaned_data.get("aff_country")
                country = getattr(country_field, "code", None)
                result = affiliation_export(year or None, country or None)

            elif "author_export" in self.request.POST:
                action_name = "author_export"
                year = form2.cleaned_data.get("author_year")
                country_field = form2.cleaned_data.get("author_country")
                country = getattr(country_field, "code", None)
                result = author_export(year or None, country or None)

            elif "year_export" in self.request.POST:
                if not self.request.user.is_superuser:
                    messages.error(
                        self.request,
                        "You do not have permission to perform this export.",
                    )
                    return self.form_invalid(form, form2, form3)

                action_name = "year_export"
                start_date = form3.cleaned_data.get("start_date") if form3 else None
                end_date = form3.cleaned_data.get("end_date") if form3 else None
                pub = (form3.cleaned_data.get("publisher_name") if form3 else None) or None

                start_date_string = start_date.strftime("%Y-%m-%d") if start_date else None
                end_date_string = end_date.strftime("%Y-%m-%d") if end_date else None
                result = year_export(start_date_string, end_date_string, pub)

            if result is None or action_name is None:
                messages.error(self.request, "No export action was recognized.")
                return self.form_invalid(form, form2, form3)

            return generate_csv_response(result, action_name)

        except Exception as ex:
            messages.error(self.request, f"There was an error: {ex}")
            return self.form_invalid(form, form2, form3)

    def form_invalid(self, form, form2, form3):
        context = self.get_context_data(form=form, form2=form2)
        if self.request.user.is_superuser:
            context["form3"] = form3 or self.third_form_class()
        return self.render_to_response(context)
