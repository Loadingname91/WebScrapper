# Create routes for web scrapping products from given urls
from kombu import uuid
from rest_framework import generics
from .tasks import web_scrapper_task, get_task_response
from .serializers import ProductSerializer
from .models import ProductResources, Product
from rest_framework.response import Response


class WebScrapperView(generics.GenericAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset = super(WebScrapperView, self).get_queryset()
        url = self.request.query_params.get('url')
        if url:
            queryset = queryset.filter(url=url)
        return queryset

    def post(self, request, *args, **kwargs):
        task_id = uuid()
        web_scrapper_task.apply_async(args=[request.data.get('url')], task_id=task_id)
        return Response(
            {"status": "success", "message": f"task id: {task_id}"}
        )

    def get(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


class GetTaskResultsView(generics.RetrieveAPIView):
    def get(self,request,*args,**kwargs):
        task_id = request.query_params.get('task_id')
        result = get_task_response(task_id)
        return Response(result)
