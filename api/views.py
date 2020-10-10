from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView
from .serializers import PostSerializer, PostDetailSerializer, PostCreateSerializer
from .models import Post
from rest_framework.pagination import PageNumberPagination


class PostPageNumberPagination(PageNumberPagination):
    page_size = 2


class Post_list(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    pagination_class = PostPageNumberPagination

class Post_detail(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

class Post_create(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

class Post_update(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    
class Post_delete(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
