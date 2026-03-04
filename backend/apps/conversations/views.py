import logging
import threading
import queue
import json as json_module
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation
from .serializers import ConversationSerializer
from agents.graph import build_graph

logger = logging.getLogger(__name__)


@api_view(['POST'])
def ask_question(request):
    """
    POST /api/ask/
    Handle user questions by running the research agent graph.
    """
    question = request.data.get('question', '').strip()

    if not question:
        return Response(
            {'error': 'Question cannot be empty'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Build and invoke the graph
        graph = build_graph()
        result = graph.invoke({
            "user_question": question,
            "plan": None,
            "search_results": None,
            "final_answer": None,
            "error": None
        })

        # Save to database
        conversation = Conversation.objects.create(
            question=question,
            plan=result.get('plan') or '',
            search_results=result.get('search_results') or '',
            answer=result.get('final_answer') or ''
        )

        # Return response
        response_data = {
            'id': str(conversation.id),
            'question': conversation.question,
            'plan': conversation.plan,
            'search_results': conversation.search_results,
            'answer': conversation.answer,
            'error': result.get('error')
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return Response(
            {'error': f'Failed to process question: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def ask_question_stream(request):
    """
    POST /api/ask/stream/
    Stream real-time agent status updates as NDJSON while processing the question.
    Each line is a JSON object with a "type" field: status | update | error | result
    """
    try:
        body = json_module.loads(request.body)
    except json_module.JSONDecodeError:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    question = body.get('question', '').strip()
    if not question:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Question cannot be empty'}, status=400)

    status_queue = queue.Queue()
    result_container = {}

    def run_graph():
        try:
            graph = build_graph()
            config = {"configurable": {"status_queue": status_queue}}
            result = graph.invoke({
                "user_question": question,
                "plan": None,
                "search_results": None,
                "final_answer": None,
                "error": None
            }, config=config)
            result_container['result'] = result
        except Exception as e:
            logger.error(f"Graph error in streaming view: {e}")
            result_container['error'] = str(e)
        finally:
            status_queue.put(None)  # sentinel to stop the generator

    thread = threading.Thread(target=run_graph, daemon=True)
    thread.start()

    def event_generator():
        yield json_module.dumps({"type": "status", "step": "init",
                                  "message": "Starting research pipeline..."}) + "\n"

        while True:
            try:
                event = status_queue.get(timeout=180)  # 3-minute per-event timeout
                if event is None:
                    break
                yield json_module.dumps(event) + "\n"
            except queue.Empty:
                yield json_module.dumps({"type": "error", "step": "timeout",
                                          "message": "Processing timed out after 3 minutes"}) + "\n"
                break

        thread.join(timeout=10)

        if 'error' in result_container:
            yield json_module.dumps({"type": "error", "step": "fatal",
                                      "message": result_container['error']}) + "\n"
        elif 'result' in result_container:
            result = result_container['result']
            try:
                conversation = Conversation.objects.create(
                    question=question,
                    plan=result.get('plan') or '',
                    search_results=result.get('search_results') or '',
                    answer=result.get('final_answer') or ''
                )
                response_data = {
                    'id': str(conversation.id),
                    'question': conversation.question,
                    'plan': conversation.plan,
                    'search_results': conversation.search_results,
                    'answer': conversation.answer,
                    'error': result.get('error')
                }
            except Exception as db_err:
                logger.error(f"DB error in streaming view: {db_err}")
                response_data = {
                    'question': question,
                    'plan': result.get('plan') or '',
                    'search_results': result.get('search_results') or '',
                    'answer': result.get('final_answer') or '',
                    'error': str(db_err)
                }
            yield json_module.dumps({"type": "result", "data": response_data}) + "\n"

    response = StreamingHttpResponse(event_generator(), content_type='application/x-ndjson')
    response['X-Accel-Buffering'] = 'no'
    response['Cache-Control'] = 'no-cache'
    return response


@api_view(['GET'])
def list_conversations(request):
    """
    GET /api/conversations/
    List the last 20 conversations.
    """
    conversations = Conversation.objects.all()[:20]
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
