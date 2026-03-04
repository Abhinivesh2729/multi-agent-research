from rest_framework import serializers
from .models import Conversation


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""

    class Meta:
        model = Conversation
        fields = ['id', 'question', 'plan', 'search_results', 'answer', 'created_at']
        read_only_fields = ['id', 'created_at']
