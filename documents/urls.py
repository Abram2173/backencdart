from django.urls import path
from . import views

urlpatterns = [
    path('flows/', views.document_flows_view, name='flows'),
]