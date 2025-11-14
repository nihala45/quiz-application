from rest_framework import serializers
from .models import Category, Quiz, Question
from .models import QuizAttempt, UserAnswer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class QuizListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True
    )
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'category_id', 'is_active', 'created_at', 'questions_count']

    def get_questions_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'category_id', 'is_active', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    category_name = serializers.CharField(source='quiz.category.name', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'quiz_title', 'category_name',
            'text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option'
        ]
        read_only_fields = ['quiz_title', 'category_name']
        
        
        
class UserAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)
    selected_option = serializers.CharField(max_length=1)

    class Meta:
        model = UserAnswer
        fields = ['question_id', 'selected_option']

class QuizAttemptSubmitSerializer(serializers.Serializer):
    answers = UserAnswerSerializer(many=True)

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    category = serializers.CharField(source='quiz.category.name', read_only=True)
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'category', 'score', 'total_questions',
                  'percentage', 'started_at', 'completed_at']
        read_only_fields = ['score', 'total_questions', 'percentage', 'started_at', 'completed_at']

class ActiveQuizListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'category_name', 'question_count']

    def get_question_count(self, obj):
        return obj.questions.count()
    
    
