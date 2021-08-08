from django.urls    import path, include
from .views         import BoardwriteView

urlpatterns = [
    path('/board-write', BoardwriteView.as_view())
]