from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView
from .serializers import PostSerializer, PostDetailSerializer, PostCreateSerializer
from .models import Post
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse, HttpResponse, FileResponse

from .utils.entity_extractor import get_auth_client, extract_entities
from .utils.calendar_utils import df_to_ics
from .utils.make_meeting_minutes import make_docx

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

class Text_extract_calendar(ListAPIView):
    def get(self, request):
        sentences = request.data['text'].split('.')
        sentences = list(filter(lambda x: len(x) > 3, sentences))
        sentences = list(map(lambda x: x.strip() + '.', sentences)) # '.' influences Azure entity recognition
        # print(sentences)
        client = get_auth_client()
        df = extract_entities(client, sentences)
        df = df_to_ics(df)
        response = df.to_dict('records')

        return JsonResponse(response, safe=False, status=200)
    
class Text_extract_minutes(ListAPIView):
    def get(self, request):
        sentences = request.data['text'].split('.')
        sentences = list(filter(lambda x: len(x) > 3, sentences))
        sentences = list(map(lambda x: x.strip() + '.', sentences))
        client = get_auth_client()
        file_name = make_docx(client, sentences)
        return FileResponse(open(file_name, 'rb'), content_type = 'text/doc')