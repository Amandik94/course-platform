from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer, UnreadCountSerializer


@extend_schema_view(
    get=extend_schema(tags=['Уведомления'], summary='Список уведомлений текущего пользователя'),
)
class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        is_read = self.request.query_params.get('is_read')
        if is_read == 'true':
            return queryset.filter(is_read=True)
        if is_read == 'false':
            return queryset.filter(is_read=False)
        return queryset


class NotificationOwnedMixin:
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema_view(
    delete=extend_schema(tags=['Уведомления'], summary='Удалить уведомление текущего пользователя'),
)
class NotificationDetailView(NotificationOwnedMixin, generics.DestroyAPIView):
    pass


class NotificationReadView(NotificationOwnedMixin, generics.GenericAPIView):
    @extend_schema(tags=['Уведомления'], responses={200: NotificationSerializer}, summary='Отметить уведомление прочитанным')
    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_as_read()
        return Response(self.get_serializer(notification).data)


class NotificationUnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Уведомления'], responses={200: UnreadCountSerializer}, summary='Количество непрочитанных уведомлений')
    def get(self, request):
        return Response({
            'count': Notification.objects.filter(user=request.user, is_read=False).count(),
        })


class NotificationReadAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Уведомления'], responses={200: UnreadCountSerializer}, summary='Отметить все уведомления прочитанными')
    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        return Response({'count': updated}, status=status.HTTP_200_OK)
