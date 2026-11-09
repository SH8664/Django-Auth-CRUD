
from rest_framework import serializers
from .models import Project, Task

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Project
        fields = '__all__'

    def validate_name(self, value):
        qs = Project.objects.filter(name=value, owner=self.context['request'].user)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)    
        if qs.exists():
            raise serializers.ValidationError("This name is already used for this owner.")
        return value
    
class ProjectDetailSerializer(ProjectSerializer):
    task_count = serializers.IntegerField(read_only=True)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['project']