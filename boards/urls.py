from django.urls    import path, include
from .views         import (
    BoardwriteView, BoardrewriteView
)

urlpatterns = [
    path('/board-write', BoardwriteView.as_view()),
    path('/board-rewrite', BoardrewriteView.as_view())
]