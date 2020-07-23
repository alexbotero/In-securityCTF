from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

#for django models
from .models import User, Challenge, UserChallenge

#for django times
from django.utils import timezone

#for random and password
from random import seed
from random import random
import hashlib

# Create your views here.
@csrf_exempt
def index(request):
    context = {
        'message': ""
    }
    #return render(request, 'challenges/index.html', context)
    if request.method == 'GET':
        return render(request, "login.html", context)
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            context['message'] = 'Usuario y clave obligatorios!!'
            return render(request, "login.html", context)
        else:
            user = User.objects.filter(username=username)
            if user:
                dbid = user[0].id
                print(dbid)
                dbpass = user[0].password
                dbsalt = user[0].salt
                pss = str(password+dbsalt).encode('utf-8')
                password = hashlib.sha256(pss).hexdigest()
                if dbpass == password:
                    request.session['logged'] = 1
                    request.session['id_user'] = dbid
                    return redirect('dashboard')
                else:
                    context['message'] = 'Usuario y clave erroneos!!'
            else:
                context['message'] = 'Usuario y clave erroneos!!'
        return render(request, "login.html", context)

def migrate(request):
    enable = True
    if enable:
        #Deleting all
        User.objects.all().delete()
        User.objects.all().delete()
        Challenge.objects.all().delete()
        Challenge.objects.all().delete()
        UserChallenge.objects.all().delete()
        UserChallenge.objects.all().delete()

        #populating challenges
        for i in range(1, 6):
            top = 50*i
            if i != 1: top = top + top*0.40
            cp = Challenge(
                name="Crypto"+str(i),
                category="Cryptography",
                reward=50*i,
                top=int(50*i),
                created=timezone.now()
            )
            cp.save()
            st = Challenge(
                name="Stego"+str(i),
                category="Steganography",
                reward=50*i,
                top=int(50*i),
                created=timezone.now()
            )
            st.save()
        
        rv = Challenge(
            name="Reversing1",
            category="Reversing",
            reward=50,
            top=50,
            created=timezone.now()
        )
        rv.save()
        #populating default users
        #any seed
        seed(5131)
        username = "admin"
        password = "1234"
        rnd = str(random()).encode('utf-8')
        salt = hashlib.sha256(rnd).hexdigest()
        pss = str(password+salt).encode('utf-8')
        password = hashlib.sha256(pss).hexdigest()
        created = timezone.now()
        #create object
        adm = User(
            username=username,
            password=password,
            salt=salt,
            created=created
        )
        adm.save()

        username = "user"
        password = "1234"
        rnd = str(random()).encode('utf-8')
        salt = hashlib.sha256(rnd).hexdigest()
        pss = str(password+salt).encode('utf-8')
        password = hashlib.sha256(pss).hexdigest()
        created = timezone.now()
        #create object
        us = User(
            username=username,
            password=password,
            salt=salt,
            created=created
        )
        us.save()

        #setting all challenges for default users
        for challenge in Challenge.objects.all():
            uc = UserChallenge(
                id_user=adm,
                id_challenge=challenge,
                point=challenge.reward,
                created=timezone.now()
            )
            uc.save()
        #print(UserChallenge.objects.filter(id_user=adm.id))
        #return
        return HttpResponse("Done")
    else:
        return HttpResponse("This is not enabled")

#Adding register 
@csrf_exempt
def register(request):
    context = {}
    context['success'] = ""
    context['message'] = ""
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        if not username:
            context['message'] = "Username mandatory"
        elif not password or not repassword:
            context['message'] = "Password mandatory"
        elif password != repassword:
            context['message'] = "Password and its repeat doesn't match"
        else:
            if User.objects.filter(username=username):
                context['message'] = "Username already exists"
            else:
                #any seed
                seed(5131)
                rnd = str(random()).encode('utf-8')
                salt = hashlib.sha256(rnd).hexdigest()
                pss = str(password+salt).encode('utf-8')
                password = hashlib.sha256(pss).hexdigest()
                created = timezone.now()
                #create object
                us = User(
                    username=username,
                    password=password,
                    salt=salt,
                    created=created
                )
                status = us.save()
                if not status:
                    context['success'] = "Account was created"
                else:
                    context['message'] = "We have errors, sorry for that"

    return render(request, "register.html", context)


@csrf_exempt
def dashboard(request):
    context = {}
    context['message'] = ''
    context['style'] = 'red'
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    
    id_user = request.session.get("id_user")

    #Validacion de flags antes de pintar retos
    if request.method == 'POST':
        context['style'] = 'green'
        context['message'] = 'Flag Correcta!!!'
        flag = request.POST.get('flag')
        response = validate_flag(id_user, flag)
        if response == -1:
            context['message'] = 'Flag ya ingresada!!!'
            context['style'] = 'green'
        elif response == 1:
            context['message'] = 'Flag correcta!!!'
            context['style'] = 'green'
        else:
            context['style'] = 'green'
            context['message'] = 'Flag Correcta!!!'
           

    user = User.objects.filter(id=id_user)
    userchallenges = UserChallenge.objects.select_related('id_challenge').filter(id_user=user[0].id)
    context['userchallenges'] = userchallenges
    score = 0
    allchallenges = Challenge.objects.all()
    for ac in allchallenges:
        ac.solved = False
        for uc in userchallenges:
            if uc.id_challenge.id == ac.id:
                ac.solved = True
                score += uc.id_challenge.reward
    context['score'] = score
    if score == 0:
        score = 50
    for ac in allchallenges:
        if score >= ac.top:
            ac.visible = True
        else:
            ac.visible = False
    context['allchallenges'] = allchallenges
    print(allchallenges)



    return render(request, "dashboard.html", context)

def validate_flag(id_user, flag):
    keys = {
        '{09e154029770bb76baea1c4bdf0f5dbd}': 'stego1',
        '{8fe69102792f7e6ff63b3966e8457a93}': 'stego2',
        '{be9f7f5419c7eb28ad6e0d2945b7d240}': 'stego3',
        '{3203edb6dcf3f131a5357e40bc0e1e58}': 'stego4',
        '{28b7539100137ba0e4af8c86a7c26db1}': 'crypto1',
        '{f4334bde8e1339f08e70e2aac99b16d6}': 'crypto2',
        '{c16a5277f0e5f17249ce71e1afaeb208}': 'crypto3',
        '{7d1496387d1adb76ae93f6604933c24f}': 'crypto4',
        '{948f95128895fce4b6ac1129d26b3350}': 'crypto5',
        '{935ee30172c2d7525b3f2063fa2c7629}': 'reversing1',
    }
    if len(flag.split("flag")) == 1:
        return 0
    flag = flag.split("flag")[1]
    if flag not in keys:
        return 0
    challenge_name = keys[flag]   
    #load user
    user = User.objects.filter(id=id_user)
    user = user[0]
    #load challenge
    challenge = Challenge.objects.filter(name=challenge_name.capitalize())
    challenge = challenge[0]

    previous = UserChallenge.objects.filter(id_user=user, id_challenge=challenge)
    if previous:
        return -1
   
    user_challenge = UserChallenge(
        id_user=user,
        id_challenge=challenge,
        point=challenge.reward,
        created=timezone.now()
    )
    if user_challenge.save():
        return 1
    else:
        return 0


def logout(request):
    request.session['logged'] = None
    del request.session['logged']
    request.session.modified = True
    return redirect('index')

def stego1(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "stego1.html", context)

def stego2(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "stego2.html", context)

def stego3(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "stego3.html", context)

def stego4(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "stego4.html", context)

def reversing1(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "reversing1.html", context)

def crypto1(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    id_user = request.session.get("id_user")
    if request.method == 'POST':
        context['style'] = 'green'
        context['message'] = 'Flag Correcta!!!'
        flag = request.POST.get('flag')
        response = validate_flag(id_user, flag)
        if response == -1:
            context['message'] = 'Flag ya ingresada!!!'
            context['style'] = 'green'
        elif response == 1:
            context['message'] = 'Flag correcta!!!'
            context['style'] = 'green'
        else:
            context['style'] = 'red'
            context['message'] = 'HP!!!'
    return render(request, "crypto1.html", context)

def crypto2(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "crypto2.html", context)

def crypto3(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "crypto3.html", context)

def crypto4(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "crypto4.html", context)

def crypto5(request):
    sess = request.session.get('logged')
    if sess != 1:
        return redirect('index')
    context = {}
    return render(request, "crypto5.html", context)