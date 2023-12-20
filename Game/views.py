from django.shortcuts import render
from django.http import HttpResponse
import fopenaiAPI1
import audioplay
import os
from django.conf import settings
import time
from openai import OpenAI
from dotenv import load_dotenv
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

turtle_assistant_id = os.getenv('TURTLE_ASSISTANT_ID')
TURTLE_ASSISTANT_ID = turtle_assistant_id

escape_assistant_id = os.getenv('ESCAPE_ASSISTANT_ID')
ESCAPE_ASSISTANT_ID = escape_assistant_id

# Create your views here.
def gamestart(request):
    if request.method =="POST":
        if request.POST.get('action') == 'start' :    
            thread_id, category, username = create_thread(request)
            if category == 'turtle':         
                request.session['turtle_thread_id'] = thread_id
                request.session['turtle'] = category
                request.session['username'] = username

                return redirect('turtlesoupgame')
            
            elif category == 'escape':
                request.session['escape_thread_id'] = thread_id
                request.session['escape'] = category
                request.session['username'] = username
            
                return redirect('escapegame')
            
        elif request.POST.get('action') == 'continue' :
            request.session['username'] = request.POST.get('username')
            if request.POST.get('user_input') == 'turtle':
                return redirect('turtlesoupgame')
            elif request.POST.get('user_input') == 'escape':
                return redirect('escapegame')
    else :
        gamect = request.GET.get('game')
        cate = {'gamect': gamect}
        return render(request, "gamestart.html", cate)
    
def turtlesoupgame(request):
    # thread = request.session.get('turtle_thread_id', 'cannot find thread id')
    # category = request.session.get('turtle', 'cannot find category')
    username = request.session.get('username', 'cannot find username')
    file_name = file_name = f'{username}turtle.txt'
    file_path = os.path.join('C:\\Users\\yooji\\python_AI\\nlp_project\\django\\threads', f'{file_name}.txt')
    with open(file_path, 'r') as file:
        thread = file.read()
        file.close()

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        run = submit_message(TURTLE_ASSISTANT_ID, thread, user_input)
        wait_on_run(run, thread)
        return redirect('turtlesoupgame')
    else :
        thread_list = answer_print(get_response(thread))
        return render(request, "turtlesoupgame.html", {'Data': thread_list})
    
def escapegame(request):
    username = request.session.get('username', 'cannot find username')
    file_name = file_name = f'{username}escape.txt'
    file_path = os.path.join('C:\\Users\\yooji\\python_AI\\nlp_project\\django\\threads', f'{file_name}.txt')
    with open(file_path, 'r') as file:
        thread = file.read()
        file.close()

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        run = submit_message(ESCAPE_ASSISTANT_ID, thread, user_input)
        wait_on_run(run, thread)
        return redirect('escapegame')
    else :
        thread_list = answer_print(get_response(thread))
        return render(request, "escapegame.html", {'Data': thread_list})

def create_thread(request):
    user_input = request.POST.get('user_input')
    username = request.POST.get('username')
    print(user_input)
    thread = client.beta.threads.create()
    print(thread.id)
    file_name = f'{username}{user_input}.txt'
    file_path = os.path.join('C:\\Users\\yooji\\python_AI\\nlp_project\\django\\threads',f'{file_name}.txt')
    with open(file_path, 'w') as file:
        file.write(str(thread.id))
    return thread.id, user_input, username

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread, order="asc")

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def answer_print(messages) :
    answer_list = []
    for m in messages :
        # 사용자의 입력과 시스템의 응답을 구분하기 위해 role을 추가하여 딕셔너리 형태 맵핑해서 저장
        answer_list.append({'content': m.content[0].text.value, 'role': m.role})
    return answer_list