from .models import Song , SongDetails , Composer
from .serializers import SongSerializer, SongDetailSerializer, ComposerSerializer
from .filters import SongFilter, SongDetailFilter, ComposerFilter
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render , get_object_or_404
from django.core.paginator import Paginator
class SongView(APIView):
    searching_fields = ["name","singer","spotify_song"]
    ordering_fields = ["song_number"]
    def get_object(self,pk=None):
        try:
            return Song.objects.get(pk=pk)
        except Song.DoesNotExist:
            return None

    def get(self,request,pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response({"error":"Object Data Not Found"},status=status.HTTP_404_NOT_FOUND)
            serializer = SongSerializer(obj)
            return Response(serializer.data)

        queryset = Song.objects.all()
        filterset = SongFilter(request.GET,queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request,queryset,self)

        order_filter = OrderingFilter()
        queryset = order_filter.filter_queryset(request, queryset, self)

        if not queryset.exists():
            return Response(
                {"success": False, "message": "No results found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = SongSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self,request,pk=None):
        if pk is not None:
            return Response({"error":"Cannot Do Post Methods in Primary Key"})

        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def patch(self,request,pk=None):
        if pk is None:
            return Response(
                {"error": "PATCH requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SongSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk=None):
        if pk is None:
            return Response(
                {"error": "PUT requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SongSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk=None):
        if pk is None:
            obj = self.get_object(pk)

            if not obj:
                return Response({"error": "Object Data Not Found"}, status=status.HTTP_404_NOT_FOUND)

            obj.delete()
            return Response({"Operation Successful": "Object Deleted"}, status=status.HTTP_200_OK)

        else:
            return Response(
                {"error": "Delete Cannot Work Without Primary Key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class SongDetailView(APIView):
    searching_fields = ["song__song", "genre", "album", "album_composer"]
    ordering_fields = ["release_date"]

    def get_object(self, pk=None):
        try:
            return SongDetails.objects.get(pk=pk)
        except SongDetails.DoesNotExist:
            return None

    def get(self, request, pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response({"error": "Object Not Found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = SongDetailSerializer(obj)
            return Response(serializer.data)

        queryset = SongDetails.objects.all()

        filterset = SongDetailFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        queryset = filterset.qs

        search_filter = SearchFilter()
        queryset = search_filter.filter_queryset(request, queryset, self)

        ordering_filter = OrderingFilter()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = SongDetailSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self,request,pk=None):
        if pk is not None:
            return Response({"error":"POST cannot work in Primary Key"})

        serializer = SongDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def patch(self, request, pk=None):
        if pk is None:
            return Response(
                {"error": "PATCH requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SongDetailSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if pk is None:
            return Response(
                {"error": "PUT requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SongDetailSerializer(obj, data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if pk is not None:
            obj = self.get_object(pk)

            if not obj:
                return Response(
                    {"error": "Object Data Not Found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            obj.delete()
            return Response(
                {"Operation Successful": "Object Deleted"},
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"error": "Delete Cannot Work Without Primary Key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ComposerView(APIView):
    searching_fields = ["name","genre"]
    ordering_fields = ["join_date","total_album","single_tracks"]
    def get_object(self,pk=None):
        try:
            return Composer.objects.get(pk=pk)
        except Composer.DoesNotExist:
            return None

    def get(self,request,pk=None):
        if pk:
            obj = self.get_object(pk)
            if not obj:
                return Response({"error":"Object Data Not Found"})
            serializer = ComposerSerializer(obj)
            return Response(serializer.data)

        queryset = Composer.objects.all()
        filterset = ComposerFilter(request.GET,queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        queryset = filterset.qs

        search_filter = SearchFilter()
        search_filter.filter_queryset(request,queryset,self)

        order_filter = OrderingFilter()
        queryset = order_filter.filter_queryset(request, queryset, self)

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ComposerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self,request,pk=None):
        if pk:
            return Response({"error":"POST Cannot Work While Primary Key"})
        serializer = ComposerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def patch(self,request,pk=None):
        if pk is None:
            return Response(
                {"error": "PATCH requires a primary key"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj = self.get_object(pk)
        if not obj:
            return Response(
                {"success": False, "message": "No record found with this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ComposerSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Data patched successfully"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def composer_list_ui(request):
    composer_queryset = Composer.objects.all().order_by('-created_at')
    paginator = Paginator(composer_queryset, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'composers': page_obj.object_list,
    }
    return render(request, "composer/composer_list.html", context)

def composer_detail_ui(request, pk):
    composer = get_object_or_404(Composer, pk=pk)
    return render(request, "composer/composer_detail.html", {
        "composer": composer
    })