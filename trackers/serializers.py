from rest_framework import serializers
from .models import Tracker, Log
from datetime import date, timedelta

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'date', 'note', 'content_link', 'is_verified', 'verification_message', 'created_at']

class TrackerSerializer(serializers.ModelSerializer):
    current_streak = serializers.SerializerMethodField()
    logs = LogSerializer(many=True, read_only=True)

    class Meta:
        model = Tracker
        fields = ['id', 'title', 'description', 'platform', 'current_streak', 'total_score', 'logs', 'created_at']

    def get_current_streak(self, obj):
        today = date.today()
        # Only count verified logs for the streak (The Pixel Pawn way)
        logs = obj.logs.filter(date__lte=today, is_verified=True).order_by('-date')
        
        streak = 0
        check_date = today
        for log in logs:
            if log.date == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            elif log.date < check_date:
                break 
        return streak