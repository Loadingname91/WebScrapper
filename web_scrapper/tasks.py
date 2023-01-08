from celery import shared_task
from celery.result import AsyncResult

from web_scrapper.serializers import ProductResourcesSerializer
from web_scrapper.utilities.web_utility import get_product_details


@shared_task(name="web_scrapper_task", bind=True)
def web_scrapper_task(self, url):
    """
    This method will scrap the product details from the given url
    :param request:
    :return:
    """
    if not url:
        return {"status": "failed", "message": "url is missing"}

    # scrap the requested url
    data = get_product_details(url)
    if not data:
        return {"status": "failed", "message": "url is not supported"}

    serializer = ProductResourcesSerializer(data=data)
    if serializer.is_valid():
        serializer.save()

        return {"status": "success",
                "message": "product details saved successfully with data {}".format(serializer.data)}
    else:
        print(serializer.errors)
        return {"status": "failed", "message": serializer.errors}


def get_task_response(task_id):
    """
    This method will return the task response
    :param task_id:
    :return:
    """
    response = AsyncResult(task_id)
    if response and response.state == "Pending":
        return {"status": "pending", "message": "task is pending"}
    elif response and response.state == "SUCCESS":
        return {"status": "success", "message": response.result}
    elif response and response.state == "FAILURE":
        return {"status": "failed", "message": response.result}
    else:
        return {"status": "failed", "message": "task is not found"}
