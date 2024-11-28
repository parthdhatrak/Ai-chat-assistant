from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import google.generativeai as genai
from .models import ChatMessage
import os
from django.conf import settings

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

@login_required
def chat_view(request):
    if request.method == 'POST':
        try:
            message = request.POST.get('message')
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)

            # Generate response from Gemini
            response = model.generate_content(message)
            
            if not response or not hasattr(response, 'text'):
                return JsonResponse({'error': 'Invalid response from AI'}, status=500)

            # Create chat message in database
            chat_message = ChatMessage.objects.create(
                user=request.user,
                message=message,
                response=response.text
            )
            
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return JsonResponse(
                {'error': 'An error occurred while processing your message'}, 
                status=500
            )
    
    chat_history = ChatMessage.objects.filter(user=request.user)
    return render(request, 'chatapp/chat.html', {'chat_history': chat_history})