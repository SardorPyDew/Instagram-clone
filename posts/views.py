from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import PostModel, PostCommentModel, PostLikeModel, CommentLikeModel
from posts.permissions import IsOwner
from posts.serializers import PostSerializer, CommentSerializer
from shared.custom_pagination import CustomPagination


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return PostModel.objects.all()


class PostCreateAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        return PostCommentModel.objects.filter(post_id=post_id)


class PostCommentCreateAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        parent_id = serializer.data['parent']
        if parent_id:
            serializer.save(parent_id=parent_id)
        post_id = self.kwargs.get('pk')
        serializer.save(user=self.request.user, post_id=post_id)


class PostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post_like = PostLikeModel.objects.filter(post_id=pk, user=self.request.user)
        if post_like.exists():
            post_like.delete()
            response = {
                "status": True,
                "message": "Successfully unliked"
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            PostLikeModel.objects.create(post_id=pk, user=self.request.user)
            response = {
                "status": True,
                "message": "Successfully liked"
            }
            return Response(response, status=status.HTTP_200_OK)


class CommentLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            comment_like = CommentLikeModel.objects.get(pk=pk)
            comment_like.delete()
            response = {
                "status": True,
                "message": "Successfully unliked from comment"
            }
            return Response(response, status=status.HTTP_200_OK)
        except CommentLikeModel.DoesNotExist:
            CommentLikeModel.objects.create(
                comment_id=pk,
                user=self.request.user
            )
            response = {
                "status": True,
                "message": "Successfully liked"
            }
            return Response(response, status=status.HTTP_200_OK)


class PostUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer = PostSerializer

    def put(self, request, pk):
        post = PostModel.objects.filter(pk=pk)
        if not post.exists():
            response = {
                "status": True,
                "message": "Invalid request",
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post.first(), data=request.data, context={'request': request})
        if serializer.is_valid():
            self.check_object_permissions(obj=post.first(), request=request)
            serializer.save()
            response = {
                "status": True,
                "message": "Successfully updated"
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            response = {
                "status": True,
                "message": "Invalid request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)