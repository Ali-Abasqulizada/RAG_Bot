from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from api.rag_service import answer_legal_query


def home_view(request):
    context = {"message": "Welcome to my Django app!"}

    return render(request, "web/index.html", context)


@api_view(["POST"])
def ask_rag_api(request):
    user_query = request.data.get("query")

    if not user_query:
        return Response(
            {"error": "Please provide a query"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = answer_legal_query(user_query)

        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
