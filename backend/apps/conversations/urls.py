from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_question, name='ask_question'),
    path('ask/stream/', views.ask_question_stream, name='ask_question_stream'),
    path('conversations/', views.list_conversations, name='list_conversations'),
]
