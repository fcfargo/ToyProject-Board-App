from django.urls import path, include
from .views       import SignupView, SigninpView

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/signin', SigninpView.as_view())
]