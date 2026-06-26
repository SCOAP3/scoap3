import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from scoap3.articles.forms import ArticlesReharvest


def post_reharvest_view(model_admin, request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can access and use this feature")

    if request.method == "POST":
        form = ArticlesReharvest(request.POST)
        if form.is_valid():
            doi = form.cleaned_data["doi"]
            dag_id = form.cleaned_data["publisher"]

            airflow_url = getattr(settings, "AIRFLOW_URL", "http://localhost:8080")
            airflow_user = getattr(settings, "AIRFLOW_USER", "admin")
            airflow_password = getattr(settings, "AIRFLOW_PASSWORD", "admin")

            endpoint = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns"
            payload = {"conf": {"doi": doi}}

            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    auth=(airflow_user, airflow_password),
                    timeout=10,
                )

                if response.status_code == 201:
                    model_admin.message_user(
                        request,
                        f"Successfully triggered DAG '{dag_id}' for DOI: {doi}.",
                        level=messages.SUCCESS,
                    )
                else:
                    model_admin.message_user(
                        request,
                        f"Airflow API Error ({response.status_code}): {response.text}",
                        level=messages.ERROR,
                    )

            except requests.RequestException as e:
                model_admin.message_user(
                    request,
                    f"Failed to connect to Airflow: {str(e)}",
                    level=messages.ERROR,
                )

            return redirect("admin:articles_article_changelist")

    else:
        form = ArticlesReharvest()

    context = dict(
        model_admin.admin_site.each_context(request),
        form=form,
        opts=model_admin.model._meta,
        title="Trigger DOI Reharvest",
    )
    return render(request, "admin/articles/trigger_reharvest.html", context)
