from django.urls import path
from api_generator.views import ActivateUser


urlpatterns = [
    path("activate/<str:uid>/<str:token>", ActivateUser.as_view(), name="activate"),

]