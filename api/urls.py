from . import views
from django.urls import path

def test_function():
    print('test')

urlpatterns = [
    #path('', views.Post_list.as_view(), name='post_list'),
    #path('post/', views.Post_list.as_view(), name='post_list'),
    #path('post/<int:pk>/', views.Post_detail.as_view(), name='post_detail'),
    #path('post/<int:pk>/update/', views.Post_update.as_view(), name='post_update'),
    #path('post/<int:pk>/delete/', views.Post_delete.as_view(), name='post_delete'),
    #path('post/create/', views.Post_create.as_view(), name='post_create'),
    #path('text/extract-calendar', views.Text_extract_calendar.as_view(), name='text_extract_calendar')
    path('text/extract-minutes', views.Text_extract_minutes.as_view(),
         name='text_extract_minutes')
]

