from django import forms

# from scoap3.misc.models import Publisher


class ArticlesReharvest(forms.Form):
    PUBLISHERS = [
        ("", "--- Select a Publisher ---"),
        ("aps_reharvest", "APS (American Physical Society)"),
        ("elsevier_reharvest", "Elsevier"),
        ("hindawi_reharvest", "Hindawi"),
        ("iop_reharvest", "IOP (Institute of Physics)"),
        ("jagiellonian_reharvest", "Jagiellonian"),
        ("oup_reharvest", "OUP (Oxford University Press)"),
        ("springer_reharvest", "Springer"),
    ]

    publisher = forms.ChoiceField(
        # queryset=Publisher.objects.all(),
        choices=PUBLISHERS,
        required=True,
        help_text="Select the publisher to trigger the corresponding DAG.",
    )
    doi = forms.CharField(
        label="DOI",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
