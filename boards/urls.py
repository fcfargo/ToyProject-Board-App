from django.urls    import path, include
from .views         import (
    BoardWriteView, BoardRewriteView, BoardDeleteView,
    BoardListView, BoardDetailView, BoardReplyView,
)

urlpatterns = [
    path('/board-write', BoardWriteView.as_view()),
    path('/board-rewrite', BoardRewriteView.as_view()),
    path('/board-delete', BoardDeleteView.as_view()),
    path('/board-list', BoardListView.as_view()),
    path('/<int:post_id>', BoardDetailView.as_view()),
    path('/board-reply', BoardReplyView.as_view())
]