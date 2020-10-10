from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField, PrimaryKeyRelatedField, DateTimeField
from .models import Post

class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('id','title','contents','create_date','update_date')

class PostDetailSerializer(ModelSerializer):
    create_date = DateTimeField(format='%Y-%m-%d %H:%M:%S.%f')
    update_date = DateTimeField(format='%Y-%m-%d %H:%M:%S.%f')
    class Meta:
        model = Post
        fields = ('id','title','contents','create_date','update_date')

class PostCreateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('title','contents','create_date')
