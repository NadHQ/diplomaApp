from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView
from django.core import serializers
from django.forms.models import model_to_dict
from .forms import AddUserPatientForm, RegisterUserForm, LoginUserForm, ProfileForm, ImageInputForm
from .models import Doctors, License, Images, Research
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse, FileResponse
import random
import keras
import cv2
import mimetypes
# import matplotlib.pyplot as plt
from tensorflow.keras import backend as K
import numpy as np
import os
import re
import json
import io
import zipfile
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm


def addPageNumber(canvas, doc):
    """
    Add the page number
    """
    page_num = canvas.getPageNumber()
    text = "%s" % page_num
    canvas.drawRightString(200 * mm, 20 * mm, text)


def createMultiPage():
    path = 'images/'
    image_list = []
    for root, directories, files in os.walk(path):
        for filenames in files:
            image_list.append(filenames)
    """
    Create a multi-page document
    """


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def iou(ytrue, ypred):
    smoothing_factor = 0.1
    # y_true_f=K.flatten(y_true)
    # y_pred_f=K.flatten(y_pred)
    intersection = K.sum(ytrue * ypred)
    combined_area = K.sum(ytrue + ypred)
    union_area = combined_area - intersection
    iou = (intersection + smoothing_factor) / (union_area + smoothing_factor)
    return iou


def jac_distance(y_true, y_pred):
    y_true = K.flatten(y_true)
    y_pred = K.flatten(y_pred)

    return -iou(y_true, y_pred)


def dice_coef(ytrue, ypred):
    smoothing_factor = 0.1
    ytrue_f = K.flatten(ytrue)
    ypred_f = K.flatten(ypred)
    intersection = K.sum(ytrue * ypred)
    ytrue_area = K.sum(ytrue)
    ypred_area = K.sum(ypred)
    combined_area = ytrue_area + ypred_area
    dice = 2 * ((intersection + smoothing_factor) / (combined_area + smoothing_factor))
    return dice


def dice_coef_loss(y_true, y_pred):
    return -dice_coef(y_true, y_pred)


# Create your views here.


def open_profile(request):
    doctor = Doctors.objects.get(licence=request.user.linecse)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form1 = ProfileForm(initial={
            'name': doctor.name,
            'second_name': doctor.second_name,
            'third_name': doctor.third_name,
            'profession': doctor.profession,
            'licence': doctor.licence
        })
        text = doctor.licence.number
        research_query = Research.objects.filter(doctor=doctor)

    return render(request, 'MriSoftware/profile.html', {'form': form1, 'licence_area': text, 'data': research_query})


@login_required
def about(request):
    return render(request, 'MriSoftware/about.html')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'MriSoftware/registration.html'
    success_url = reverse_lazy('login')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'MriSoftware/login.html'

    def get_success_url(self):
        return reverse_lazy('profile')


# def registration(request):
#     return render(request, 'MriSoftware/registration.html')


def research(request):
    thresh_level = 120
    thresh_for_masks = 100
    if request.method == "POST":
        for_masking = []
        image_dict = {}
        object_research = Research.objects.get(id=request.session.get('object_research_1'))
        data = request.POST
        image_list = request.FILES.getlist('images')
        # print(image_list)

        for images in image_list:
            img = Images.objects.create(
                research=object_research,
                image=images
            )
            for_masking.append(img.image.url)
            image_dict[img.image.url] = img
        print(image_dict)

        model = keras.models.load_model('attUNET-brain-mriv5.h5',
                                        custom_objects={"iou": iou, "dice_coef": dice_coef})
        os.mkdir('media/user_{0}/{1}/masked/'.format(object_research.doctor.licence.number,
                                                     object_research.patient.pass_number))
        for i in for_masking:
            new_i = i.split('/')
            new_i = new_i[len(new_i) - 1]
            new_i = new_i.split('.')
            new_i = new_i[0]
            # pathimage = 'tmp/'+new_i + '_masked.jpg'
            pathimage = 'media/user_{0}/{1}/masked/{2}_masked.jpg'.format(object_research.doctor.licence.number,
                                                                          object_research.patient.pass_number, new_i)
            pathimage2 = 'user_{0}/{1}/masked/{2}_masked.jpg'.format(object_research.doctor.licence.number,
                                                                     object_research.patient.pass_number, new_i)
            image = cv2.imread('/home/zephyr/dev/Python/diplomaWork/Programm/MedivhProject' + i)
            img = cv2.resize(image, (256, 256))
            img = img / 255
            img = img[np.newaxis, :, :, :]
            pred = model.predict(img)
            result_image = np.uint8(np.squeeze(pred) * 255)
            # cv2.imwrite(f'{path}{random.randint(1, 10000)}.jpg', result_image)
            ret, thresh = cv2.threshold(result_image, thresh_level, 230, cv2.THRESH_BINARY)
            # cv2.imwrite(path + 'segm_' + i, thresh)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            image_copy = image.copy()
            cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(255, 0, 0), thickness=3)
            image_resize = cv2.resize(image_copy, (512, 512), interpolation=cv2.INTER_AREA)
            cv2.imwrite(pathimage, image_resize)
            object_to_write = image_dict[i]
            object_to_write.masked = pathimage2
            object_to_write.save()

        query = Images.objects.filter(research=object_research)
        image_paths_list = []
        for i in query:
            image_paths_list.append(i.masked.url)
        context = {
            'ima': image_paths_list
        }
        dataJson = json.dumps(context)
        return render(request, 'MriSoftware/main.html', {'data': dataJson})
    return render(request, 'MriSoftware/main.html')


def archive(request):
    object_research = Research.objects.get(id=request.session.get('object_research_1'))
    archive_name = "media/user_{0}/{1}/archive.zip".format(object_research.doctor.licence.number,
                                                      object_research.patient.pass_number)
    second_path = "user_{0}/{1}/archive.zip".format(object_research.doctor.licence.number,
                                                   object_research.patient.pass_number)
    print(object_research)
    image_paths_list = []
    query = Images.objects.filter(research=object_research)
    for i in query:
        image_paths_list.append(i.masked.url[1:])
        image_paths_list.append(i.image.url[1:])
    print(image_paths_list)
    file = zipfile.ZipFile(archive_name, 'w')
    for i in image_paths_list:
        file.write(i)
    file.close()
    object_research.file = second_path
    object_research.save()
    return redirect('profile')


def report(request):
    object_research = Research.objects.get(id=request.session.get('object_research_1'))
    pdf_name = "media/user_{0}/{1}/report.pdf".format(object_research.doctor.licence.number,
                                                                   object_research.patient.pass_number)
    second_path = "user_{0}/{1}/report.pdf".format(object_research.doctor.licence.number,
                                                                    object_research.patient.pass_number)
    query = Images.objects.filter(research=object_research)
    image_paths_list = []
    for i in query:
        image_paths_list.append(i.masked.url)
    doc = SimpleDocTemplate(filename=pdf_name,
                            pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    Story = []

    for i, k in zip(range(1, len(image_paths_list)), image_paths_list):
        ptext = '<font size="14">REPORT</font>'
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        ptext = '<font size="12">NAME</font>'
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        ptext = '<font size="12">SECOND NAME</font>'
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        ptext = '<font size="12">THIRD NAME</font>'
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        ptext = '<font size="12">PASS NUMBER</font>'
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        Story.append(Spacer(1, 12))
        Story.append(Spacer(1, 12))
        Story.append(Image(image_paths_list[i][1:], 400, 400))
        ptext = '<font size="12">{0}</font>'.format(image_paths_list[i][1:])
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(PageBreak())
    doc.build(Story, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
    object_research.report = second_path
    object_research.save()
    return HttpResponse('Done')


def start(request):
    if request.method == 'POST':
        something = request.body.decode('utf-8')
        something2 = request.headers
        form = AddUserPatientForm(request.POST)
        if form.is_valid():
            m = form.save()
            send_object = Research.objects.create(
                doctor=Doctors.objects.get(licence=request.user.linecse),
                patient=m
            )
            object_research = send_object.id
            request.session['object_research_1'] = object_research
            # return render(request, 'MriSoftware/main.html', {'object': object_research})
            return redirect('research')
    else:

        form = AddUserPatientForm()
    return render(request, 'MriSoftware/start.html', {'form': form})

# def login(request):
#     return render(request, 'MriSoftware/login.html')
