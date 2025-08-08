from django import forms
from django_select2.forms import ModelSelect2Widget

from scoap3.misc.models import Country


class CountryWidget(ModelSelect2Widget):
    search_fields = ["code__icontains", "name__icontains"]


class Country2Widget(ModelSelect2Widget):
    search_fields = ["code__icontains", "name__icontains"]


class AffiliationExportForm(forms.Form):
    aff_year = forms.IntegerField(label="Year", required=True)
    aff_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=Country2Widget,
        label="Country",
        required=True,
    )


class AuthorExportForm(forms.Form):
    author_year = forms.IntegerField(label="Year", required=True)
    author_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=CountryWidget,
        label="Country",
        required=True,
    )


class YearExportForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Start date",
        help_text="Leave blank for no start date",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="End date",
        help_text="Leave blank for no end date",
    )
    publisher_name = forms.CharField(
        required=False,
        max_length=200,
        label="Publisher name",
        help_text="Leave blank for all publishers",
    )
