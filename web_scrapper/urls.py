from django.urls import path

from web_scrapper.views import WebScrapperView, GetTaskResultsView

urlpatterns = [
    path('parse_url/', WebScrapperView.as_view(), name="parse_url"),
    path('get_task_results/', GetTaskResultsView.as_view(), name="get_task_results"),
]
