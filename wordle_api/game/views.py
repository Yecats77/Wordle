from django.http import JsonResponse, HttpResponse
import game.utils as utils
import json
from rest_framework.views import APIView

class user_submit_word(APIView):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            word = request.POST.get('word') # request.data['word']
            
            return JsonResponse({
                'result': 'true',
                'message': 'valid input',
            })

        return HttpResponse("Method Not Allowed", status=405)
