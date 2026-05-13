# visual_search/urls.py
# URL routes for the visual_search app.
# Mount this under /visual-search/ in the main project urls.py.

from django.urls import path
from .views import VisualSearchView, VisualSearchPageView

urlpatterns = [
    path("", VisualSearchPageView.as_view(), name="visual_search_page"),
    path("api/", VisualSearchView.as_view(), name="visual_search_api"),
]