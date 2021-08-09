from django.urls    import path, include
from .views         import (
    BoardWriteView, BoardRewriteView, BoardDeleteView,
    BoardListView,
)

urlpatterns = [
    path('/board-write', BoardWriteView.as_view()),
    path('/board-rewrite', BoardRewriteView.as_view()),
    path('/board-delete', BoardDeleteView.as_view()),
    path('/board-list', BoardListView.as_view()),
]