from django.urls import path
from .views import VisualSearchView, VisualSearchPageView

urlpatterns = [
    path("", VisualSearchPageView.as_view(), name="visual_search_page"),
    path("api/", VisualSearchView.as_view(), name="visual_search_api"),
]