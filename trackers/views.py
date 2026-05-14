# trackers/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from .models import Tracker, Log
from .serializers import TrackerSerializer, LogSerializer
from datetime import date
import requests
from bs4 import BeautifulSoup

class TrackerViewSet(viewsets.ModelViewSet):
    serializer_class = TrackerSerializer

    def get_queryset(self):
        return Tracker.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def log_action(self, request, pk=None):
        tracker = self.get_object()
        url = request.data.get('content_link')
        log_date = request.data.get('date', date.today())
        
        is_verified = False
        msg = "Pending verification"

        if url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    is_verified = True 
                    msg = "Link verified"
                    tracker.total_score += 10 
                    tracker.save()
            except:
                msg = "Link unreachable"
        
        log = Log.objects.create(
            tracker=tracker,
            date=log_date,
            content_link=url,
            proof_image=request.FILES.get('proof_image'),
            is_verified=is_verified,
            verification_message=msg
        )
        # Using LogSerializer here clears the yellow line warning
        return Response(LogSerializer(log).data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        # Using Sum here clears the yellow line warning
        top_users = Tracker.objects.values('user__username')\
            .annotate(score=Sum('total_score'))\
            .order_by('-score')[:10]
        return Response(top_users)