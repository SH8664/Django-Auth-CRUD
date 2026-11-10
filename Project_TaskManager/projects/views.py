from rest_framework import viewsets , status , filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Project,Task
from .serializers import ProjectSerializer , TaskSerializer , ProjectDetailSerializer



# Create your views here.


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    filterset_fields = ["status"]


    @action(detail=True, methods=["get" , "post"])
    def tasks(self, request, pk=None):
        if request.method == "GET":
            project = self.get_object()
            # if project.owner != self.request.user:
            #     return Response({"error": "You are not the owner of this project."}, status=status.HTTP_403_FORBIDDEN)
            tasks = project.task_set.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else :
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(project=self.get_object())
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        project = self.get_object()
        # if project.owner != self.request.user:
        #                 return Response({"error": "You are not the owner of this project."}, status=status.HTTP_403_FORBIDDEN)
        rows = project.task_set.values("status").annotate(count=Count("status"))
        counts = {value: 0 for value, _ in Task.status.field.choices}   
        counts.update({row["status"]: row["count"] for row in rows})    
        return Response(counts, status=status.HTTP_200_OK)
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectSerializer


    def get_queryset(self):
        if self.action == "retrieve":
            return Project.objects.filter(owner=self.request.user).annotate(task_count=Count("task"))
        return Project.objects.filter(owner=self.request.user)


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
            instance.is_deleted = True
            instance.save(update_fields=["is_deleted"])    

class TaskView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["title"]

    ordering_fields = ["created_at", "due_date" , "priority"]
    filterset_fields = ["status", "priority" , "due_date"]

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user)