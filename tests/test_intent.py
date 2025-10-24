"""Tests for intent detection."""

import pytest
from app.services.intent import intent_detection_service


class TestIntentDetection:
    """Test intent detection service."""

    def test_open_channel_intent(self):
        """Test open channel intent detection."""
        utterance = "Open WhatsApp channel for Retail Banking and enable card block"

        result = intent_detection_service.detect_intent(
            utterance=utterance,
            channel="web",
            locale="en-IN",
            trace_id="test-001",
        )

        assert result.intent == "open_channel"
        assert result.confidence >= 0.7
        assert not result.ood

    def test_faq_intent(self):
        """Test FAQ intent detection."""
        utterance = "What are NEFT transfer charges?"

        result = intent_detection_service.detect_intent(
            utterance=utterance,
            channel="web",
            locale="en-IN",
            trace_id="test-002",
        )

        assert result.intent == "faq_policy"
        assert result.confidence >= 0.7
        assert not result.ood

    def test_ood_detection(self):
        """Test out-of-domain detection."""
        utterance = "What's the weather like today?"

        result = intent_detection_service.detect_intent(
            utterance=utterance,
            channel="web",
            locale="en-IN",
            trace_id="test-003",
        )

        # Should be classified as OOD or have low confidence
        assert result.ood or result.confidence < 0.6

    def test_close_channel_intent(self):
        """Test close channel intent."""
        utterance = "I want to close my Telegram channel"

        result = intent_detection_service.detect_intent(
            utterance=utterance,
            channel="web",
            locale="en-IN",
            trace_id="test-004",
        )

        assert result.intent == "close_channel"
        assert result.confidence >= 0.7


class TestEntityExtraction:
    """Test entity extraction."""

    def test_extract_channel_entities(self):
        """Test channel entity extraction."""
        utterance = "Open WhatsApp channel for Retail Banking"

        entities = intent_detection_service.extract_entities(
            utterance=utterance,
            intent="open_channel",
            kb_context="Available channels: WhatsApp, Telegram, Email",
        )

        # Should extract channel
        assert entities.channel is not None

    def test_extract_operation_entities(self):
        """Test operation entity extraction."""
        utterance = "Enable card block and balance inquiry"

        entities = intent_detection_service.extract_entities(
            utterance=utterance,
            intent="open_channel",
            kb_context="Operations: card_block, balance_inquiry, fund_transfer",
        )

        # Should extract operations
        assert entities.operations is not None or entities.operation is not None


# API Tests
class TestIntentAPI:
    """Test intent API endpoints."""

    def test_detect_intent_endpoint(self, client):
        """Test /intent/v1/detect endpoint."""
        response = client.post(
            "/intent/v1/detect",
            json={
                "utterance": "Open WhatsApp channel for Retail Banking",
                "channel": "web",
                "locale": "en-IN",
                "tenant": "test-tenant",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "intent" in data
        assert "confidence" in data
        assert "entities" in data
        assert "traceId" in data

    def test_simulate_endpoint(self, client):
        """Test /intent/v1/simulate endpoint."""
        response = client.post(
            "/intent/v1/simulate",
            json={
                "utterances": [
                    "Open WhatsApp channel",
                    "What are NEFT charges?",
                    "Close my account",
                ],
                "tenant": "test-tenant",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert len(data["results"]) == 3
