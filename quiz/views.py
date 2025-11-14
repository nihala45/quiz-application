from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import Category, Quiz, Question
from .serializers import (
    CategorySerializer,
    QuizListSerializer,
    QuizDetailSerializer,
    QuestionSerializer,
    ActiveQuizListSerializer,        
    QuizAttemptSerializer,            
    QuizAttemptSubmitSerializer,
    UserAnswerSerializer,
    QuizAttempt,
    UserAnswer
)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']

    def get_serializer_class(self):
        return CategorySerializer

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Category updated.", "category": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Category deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({"message": "Toggled.", "is_active": obj.is_active})

    @action(detail=False, methods=['post'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        is_active = request.data.get('is_active')
        if not ids or is_active is None:
            return Response({"error": "ids and is_active required."}, status=status.HTTP_400_BAD_REQUEST)
        updated = Category.objects.filter(id__in=ids).update(is_active=is_active)
        return Response({"message": f"{updated} updated.", "is_active": is_active})


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('category').all().order_by('-created_at')
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'category__name']
    filterset_fields = ['category', 'is_active']

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Quiz updated.", "quiz": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Quiz deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        return Response({"message": "Toggled.", "is_active": obj.is_active})

    @action(detail=False, methods=['post'], url_path='bulk-status')
    def bulk_status(self, request):
        ids = request.data.get('ids', [])
        is_active = request.data.get('is_active')
        if not ids or is_active is None:
            return Response({"error": "Required fields missing."}, status=status.HTTP_400_BAD_REQUEST)
        updated = Quiz.objects.filter(id__in=ids).update(is_active=is_active)
        return Response({"message": f"{updated} quizzes updated.", "is_active": is_active})


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('quiz__category').all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d']
    filterset_fields = ['quiz', 'quiz__category', 'correct_option']

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Question updated.", "question": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Question deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='toggle-correct')
    def toggle_correct(self, request, pk=None):
        question = self.get_object()
        options = ['A', 'B', 'C', 'D']
        idx = options.index(question.correct_option)
        question.correct_option = options[(idx + 1) % 4]
        question.save(update_fields=['correct_option'])
        return Response({"correct_option": question.correct_option})

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "ids required."}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Question.objects.filter(id__in=ids).delete()
        return Response({"message": f"{deleted} questions deleted."})

    @action(detail=False, methods=['post'], url_path='bulk-correct')
    def bulk_correct(self, request):
        ids = request.data.get('ids', [])
        correct_option = request.data.get('correct_option')
        if not ids or correct_option not in 'ABCD':
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)
        updated = Question.objects.filter(id__in=ids).update(correct_option=correct_option)
        return Response({"message": f"{updated} updated.", "correct_option": correct_option})
    
    

class QuizUserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active_quizzes(self, request):
        quizzes = Quiz.objects.filter(is_active=True).prefetch_related('questions')
        serializer = ActiveQuizListSerializer(quizzes, many=True)
        return Response(serializer.data)

   
    @action(detail=True, methods=['get'], url_path='start')
    def start_quiz(self, request, pk=None):
        quiz = Quiz.objects.filter(id=pk, is_active=True).first()
        if not quiz:
            return Response({"error": "Quiz not found or inactive"}, status=404)

        questions = quiz.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response({
            "quiz_id": quiz.id,
            "title": quiz.title,
            "total_questions": questions.count(),
            "questions": serializer.data
        })

  
    @action(detail=True, methods=['post'], url_path='submit')
    def submit_quiz(self, request, pk=None):
        quiz = Quiz.objects.filter(id=pk, is_active=True).first()
        if not quiz:
            return Response({"error": "Quiz not found or inactive"}, status=404)

        serializer = QuizAttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        answers_data = serializer.validated_data['answers']

        with transaction.atomic():
          
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                score=0,
                completed_at=timezone.now()
            )

            correct_count = 0
            for answer_data in answers_data:
                question_id = answer_data['question_id']
                selected = answer_data['selected_option'].upper()

                try:
                    question = Question.objects.get(id=question_id, quiz=quiz)
                except Question.DoesNotExist:
                    continue

                is_correct = (question.correct_option == selected)

                if is_correct:
                    correct_count += 1

                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected,
                    is_correct=is_correct
                )
            attempt.score = correct_count
            attempt.save()

        return Response({
            "message": "Quiz submitted successfully!",
            "attempt_id": attempt.id,
            "score": attempt.score,
            "total": attempt.total_questions,
            "percentage": attempt.percentage
        })

    
    @action(detail=False, methods=['get'], url_path='my-attempts')
    def my_attempts(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz__category')
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

  
    @action(detail=True, methods=['get'], url_path='attempt-detail')
    def attempt_detail(self, request, pk=None):
        try:
            attempt = QuizAttempt.objects.get(id=pk, user=request.user)
        except QuizAttempt.DoesNotExist:
            return Response({"error": "Attempt not found"}, status=404)

        answers = attempt.answers.select_related('question').all()
        answer_data = []
        for ua in answers:
            q = ua.question
            answer_data.append({
                "question_text": q.text,
                "your_answer": ua.selected_option,
                "correct_answer": q.correct_option,
                "is_correct": ua.is_correct,
                "options": {
                    "A": q.option_a,
                    "B": q.option_b,
                    "C": q.option_c,
                    "D": q.option_d
                }
            })

        attempt_serializer = QuizAttemptSerializer(attempt)
        return Response({
            "attempt": attempt_serializer.data,
            "answers": answer_data
        })
        
        
        
        
        
        