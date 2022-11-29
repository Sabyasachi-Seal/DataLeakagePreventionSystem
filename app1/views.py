from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ChangepwdForm, DocumentForm, DetectorUploadForm, AccessLogForm
from login.models import LoginDetails
from app1.models import Document as doc, DetectorUpload, AccessLog
from django.db.models.signals import post_save

from login.models import LoginDetails as Users
#from myapp.models import MyModel
from django.views.decorators.cache import cache_control
import cv2
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
import subprocess
import codecs
from Crypto.Cipher import AES
from django.db.models import Q
from django.contrib import messages
import os
import base64
import random
import time

# Create your views here.
k = []
logs = [[0, 0], [0, 0], [0, 0], [0, 0]]


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userhome(request):
    try:
        username = request.session['username']
        designation = request.session['access']
        clientid = request.session['clientid']
        levels = ['public', 'private', 'confidential', 'topsecret']
        context = {
            'username': username,
            'designation': levels[designation % 4 - 1],
            'nbar': 'home',
        }
    except:
        return HttpResponseRedirect('/')
    if designation == 5:
        del request.session['username']
        return HttpResponseRedirect('/')
    return render(request, 'app1/userHome.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detectorhome(request):
    try:
        username = request.session['username']
        designation = request.session['access']
        clientid = request.session['clientid']
        context = {
            'username': username,
            'nbar': 'home',
        }
    except:
        return HttpResponseRedirect('/')
    if designation != 5:
        del request.session['username']  # end the session
        return HttpResponseRedirect('/')  # redirect to login page
    return render(request, 'app1/detectorHome.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def changepassword(request):
    try:
        username = request.session['username']
        designation = request.session['access']
        clientid = request.session['clientid']
    except:
        return HttpResponseRedirect('/')
    levels = ['public', 'private', 'confidential', 'topsecret']
    if request.method == 'POST':
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            current = form.cleaned_data['current']
            new = form.cleaned_data['new']
            reenter = form.cleaned_data['reenter']

            q = LoginDetails.objects.filter(username=username)
            print(q)
            if q.password == current:
                if new == reenter:
                    q.password = new
                    q.save()
                else:
                    return HttpResponse("new and reentered password doesn't match")
            else:
                return HttpResponse("incorrect password")
    else:
        form = ChangepwdForm()

    context = {
        'form': form,
        'username': username,
        'designation': levels[designation % 4 - 1],
        'nbar': 'changepass'
    }
    if designation == 5:
        return render(request, 'app1/detector_changePassword.html', context)
    else:
        return render(request, 'app1/user_changePassword.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def modelformupload(request):
    try:
        username = request.session['username']
        designation = request.session['access']
        clientid = request.session['clientid']
    except:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            if request.POST['accesslevel'] > str(designation):
                return HttpResponse("Access level not allowed")
            else:
                form.save()
                q = doc.objects.last()
                q.author = clientid
                q.accesslevel = designation
                q.save()

            return HttpResponseRedirect('/user/userhome')
    else:
        form = DocumentForm()
    levels = ['public', 'private', 'confidential', 'topsecret']
    context = {
        'form': form,
        'designation': levels[designation % 4 - 1],
        'nbar': 'uploaddoc',
        'username': username,
    }
    if designation == 5:
        del request.session['username']
        return HttpResponseRedirect('/')
    return render(request, 'app1/user_uploadDocument.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def accessLogs(request):
    try:
        username = request.session['username']
        clientid = request.session['clientid']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    global logs
    levels = ['public', 'private', 'confidential', 'topsecret']
    q = doc.objects.all()
    context = {
        'nbar': 'history',
        'data': q,
        'designation': designation,
        'username': username,
    }
    print(q)
    #form = AccessLogForm(request.GET, name, out , )

    return render(request, "app1/detector_checkDocument.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def displayfiles(request):
    try:
        username = request.session['username']
        clientid = request.session['clientid']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    q = doc.objects.all()
    levels = ['public', 'private', 'confidential', 'topsecret']
    context = {
        'data': q,
        'nbar': 'displaydoc',
        'designation': levels[designation % 4 - 1],
        'username': username,
    }
    global logs
    n = random.randint(0, 100)
    # sender = Users.objects.get(username=context['username'])
    # recipient = Users.objects.get(username='john')
    # print(sender, recipient)

    # message = "This is an simple message"
    # notify.send(sender=sender, recipient=recipient, verb='Message',
    #             description=message)
    #messages.info(request, 'Your password has been changed successfully!')
    # notify2.init('Attention')
    # n = notify2.Notification('Attention',f'User { context["username"]} has accessed the file {request.POST.get("filename")}')
    # n.show()
    # send(context['username'],'john','Message')
    if request.method == 'POST':
        # filename is name attribute of the button clicked in template
        if request.POST.get('filename'):
            name = request.POST.get('filename')
            out = f"documents/document-output-{n}.pdf"
            val = modify_file(name, clientid, n,designation)
            q = AccessLog()
            q.filename = name
            q.accesslevel = context['designation']
            q.document = out
            q.save()
            if val == "success":
                return HttpResponseRedirect("/media/" + out)
            else:
                return HttpResponse("Embed failure")

    # if designation == 5:
    # 	del request.session['username']
    # 	return HttpResponseRedirect('/')
    return render(request, "app1/user_searchDocument.html", context)


def modify_file(filename, clientid, n,designation):
    q = LoginDetails.objects.filter(clientid=clientid)[0]
    s = [i for i in doc.objects.filter(document=filename)]
    s= s[-1]
    cipher = q.cipher_text
    hash1 = q.hash_text
    owner = s.author
    designation = s.accesslevel
    # cipher embedding
    print(cipher)
    encryption_suite = AES.new(
        'thisisorignalkey'.encode('utf-8'), AES.MODE_CBC, 'thisisinitvector'.encode('utf-8'))
#c = pad(c.encode(), AES.block_size)
    plain = encryption_suite.encrypt(cipher.encode('utf-8'))
    cipher = base64.b64encode(plain).decode('utf-8')
    pixel_array = [ord(c) for c in cipher]
    print(pixel_array)
    #del pixel_array[-1]
    folder = os.getcwd()
    print(f'{folder}\media\{filename}')
    t = filename
    filename = 'documents\index.jpeg'
    img = cv2.imread(f'{folder}\media\{filename}')
    owner_l = [ord(c) for c in owner]
    img.itemset((2,3,0), owner_l[0])
    img.itemset((3,3,0), owner_l[1])
    img.itemset((4,3,0), owner_l[2])
    img.itemset((9,2,0), designation)
    # print(filename)
    x = 55
    y = 10
    for i in range(len(pixel_array) - 1, -1, -1):
        img.itemset((x, y, 0), pixel_array[i])
        y += 1
    #print(img.item(55, 10, 0), img.item(55, 11, 0), img.item(55, 12, 0))
    # hash embedding
    print(hash1)
    pixel_array1 = [ord(c) for c in hash1]
    print('pixel_arr', pixel_array1)
    x = 58
    y = 10
    for i in range(len(pixel_array1) - 1, -1, -1):
        if (y >= img.shape[1]):
            y = 0
            x = x + 1

        img.itemset((x, y, 0), pixel_array1[i])
        y = y + 1
        print('inside for loop')
    cv2.imwrite(f'{folder}\media\documents\image_small_hash.png', img)

    # embedding process
    print('image_saved')
    c = canvas.Canvas(f"{folder}\media\documents\watermark.pdf")
    c.drawImage(f"{folder}/media/documents/image_small_hash.png",
                0, 0, preserveAspectRatio=True)
    c.save()
    filename = t
    output = PdfFileWriter()
    newurl = f"{folder}/media/" + filename
    input1 = PdfFileReader(open(newurl, "r+b"))
    num_pages = input1.getNumPages()
    watermark = PdfFileReader(
        open(f"{folder}/media/documents/watermark.pdf", "r+b"))

    for pg in range(0, num_pages):
        page = input1.getPage(pg)
        page.mergePage(watermark.getPage(0))
        output.addPage(page)

    # finally, write "output" to document-output.pdf
    outputStream = open(
        f"{folder}/media/documents/document-output-{n}.pdf", "w+b")
    output.write(outputStream)
    outputStream.close()
    return ("success")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkdocument(request):
    if(k):
        messages.error(request, "Error: " + k.pop() + " is culprit")
    try:
        username = request.session['username']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    if designation != 5:
        del request.session['username']  # end the session
        return HttpResponseRedirect('/')  # redirect to login page
    if request.method == 'POST':
        form = DetectorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            extraction()
        return HttpResponseRedirect('/user/history')

    else:
        form = DetectorUploadForm()

    context = {
        'username': username,
        'nbar': 'checkdoc',
        'form': form,
    }
    return render(request, "app1/detector_checkDocument.html", context)


def extraction():
    q = DetectorUpload.objects.last()
    name = str(q.document)
    folder = os.getcwd()
    print(name)
    document_location = os.path.join(folder + '\media')
    fixed_name = name.split('/')[1]
    file_loc = os.path.join(document_location + f'\detector\{fixed_name}')
    logo_loc = os.path.join(document_location + "\detector\z" )
    print(logo_loc, file_loc)
    # logo extraction from document
    subprocess.call(["pdfimages", "-j", "-l", "1", file_loc, logo_loc])
    time.sleep(1)
    print('logo is extracted')
    # cipher extraction from logo
    print(document_location + '\detector\z-0000.ppm')
    try:
        im = cv2.imread(document_location + '\detector\z-0000.ppm')
        cipher = []
        print(im.shape)
        owner = [im[2,3,0], im[3,3,0], im[4,3,0]]
        owner_n = ''.join(chr(c) for c in owner)
        owner_d = im[9,2,0]
        for i in range(0, 24):
            cipher.append(im[55, i+10, 0])
            # cipher.append(im[58,i+10,0])
        print(cipher)
        cipher = ''.join(chr(c) for c in cipher)
        cipher = cipher[::-1]
        print(cipher)
        #cipher=cipher + '\n'
        #[61, 61, 65, 115, 100, 54, 90, 73, 81, 101, 57, 100, 113, 68, 112, 88]
        #[98, 84, 109, 115, 77, 73, 77, 117, 88, 112, 68, 113, 100, 57, 101, 81, 73, 90, 54, 100, 115, 65, 61, 61]
        # decryption of cipher
        #base64_data = cipher.encode('utf-8')
        #base64_data = f'{cipher}'
        decryption_suite = AES.new(
            'thisisorignalkey'.encode('utf-8'), AES.MODE_CBC, 'thisisinitvector'.encode('utf-8'))
        cipher_text = decryption_suite.decrypt(
            base64.b64decode(cipher)).decode('utf-8')
        print('base64', cipher_text)
        #cipher_text = base64_data[::-1]
        # cipher_text = codecs.decode(base64_data, 'base64')
        # decryption_suite = AES.new('this is a key123', AES.MODE_CBC, 'This is an IV456')
        # plain = decryption_suite.decrypt(cipher_text)
        # plain = plain.decode('utf-8')
        # extaction of hash from logo
        print('done')
        x = 58
        y = 10
        reverse_hash = []
        for i in range(0, 128, 1):
            if(y >= im.shape[1]):
                y = 0
                x = x+1
            reverse_hash.append(im[x, y, 0])
            y = y+1
        hash = reverse_hash[::-1][-3:]
        hash = ''.join(chr(c) for c in hash)  # join characters
        print(hash)

        flag = True
        for i in LoginDetails.objects.filter():
            print('FromLoop', cipher_text, i.cipher_text, i.designation, owner_d)
            if cipher_text == i.cipher_text and i.hash_text == hash:
                culprit = i
                print(culprit.clientid, culprit.username, culprit.hash_text)

                if culprit.hash_text == hash:
                    print('here',culprit.clientid, owner_n, owner_d, culprit.designation)
                    if culprit.clientid != owner_n:
                        flag = False
                        if culprit.designation < owner_d:
                        
                            print("Culprit's name is: {}".format(culprit.username))
                            q.username = culprit.username
                            q.designation = culprit.designation
                            q.m = hash
                            q.mdash = culprit.hash_text
                            q.clientid = culprit.clientid
                            q.status = 'Leaked'
                            q.save()
                        else:
                            q.status = 'Veiwed by senior'
                            q.username = culprit.username
                            q.designation = culprit.designation
                            q.save()
                            
                    else:
                        q.status = 'Owner'
                        q.username = culprit.username
                        q.designation = culprit.designation
                        q.save()
                        flag = False

        if flag:
            print("Not Leaked")
            q.status = 'No'
            q.save()
        os.remove(document_location + '\detector\z-0000.ppm')
    except:
        q.status = 'Not Accessed'
        q.save()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def history(request):
    try:
        username = request.session['username']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    if designation != 5:
        del request.session['username']  # end the session
        return HttpResponseRedirect('/')  # redirect to login page

    #q = DetectorUpload.objects.exclude(status='Not Viewed').order_by("-uploaded_at")
    q = DetectorUpload.objects.all()
    context = {
        'nbar': 'history',
        'data': q,
        'designation': designation,
        'username': username,
    }

    return render(request, 'app1/detector_history.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deletefile(request):
    try:
        username = request.session['username']
        clientid = request.session['clientid']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    q = doc.objects.filter(author=clientid)  # make it author
    levels = ['public', 'private', 'confidential', 'topsecret']
    context = {
        'data': q,
        'nbar': 'deletedoc',
        'designation': levels[designation % 4 - 1],
        'username': username,
    }
    print(type(designation))
    global logs
    document_location = '/'.join(os.path.dirname(__file__).split('/')
                                 [:-1]) + '/media/'
    if request.method == 'POST':
        # filename is name attribute of the button clicked in template
        if request.POST.get('filename'):
            name = request.POST.get('filename')
            del_location = document_location + name
            print(del_location)
            delfile = doc.objects.get(document=name)
            if(designation == 1 and delfile.accesslevel != "$public"):
                k.append(username)
            doc.objects.get(document=name).delete()
            for i in logs:
                if i[0] == name:
                    logs.remove(i)
            subprocess.call(["rm", del_location])

    if designation == 5:
        del request.session['username']
        return HttpResponseRedirect('/')
    return render(request, 'app1/user_deleteDocument.html', context)
