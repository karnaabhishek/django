from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response    
import requests
from rest_framework import views, permissions
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice# Create your views here.
from rest_framework import status
from django.core.mail import send_mail
import qrcode
from django.template import Context
from django.template.loader import render_to_string
from django.shortcuts import redirect, render
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage



class ActivateUser(GenericAPIView):

    def get(self, request, uid, token, format = None):
        payload = {'uid': uid, 'token': token}
        print(payload)
        url = "http://localhost:8000/auth/users/activation/"
        response = requests.post(url, data = payload)

        if response.status_code == 204:
            return Response({}, response.status_code)
        else:
            return Response(response.json())

def get_user_totp_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device

class TOTPCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        user = request.user
        device = get_user_totp_device(self, user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        print('email'+ user.email)

        
        img = qrcode.make(url)
        type(img)  # qrcode.image.pil.PilImage.
        img.save("api_generator/image/some_file.png")
        img_url = "/home/abhishek/Desktop/new/django_auth/api_generator/image/some_file.png"
        context = {'img_url': img_url}
        
        html_content = render_to_string('email/template.html', context)
        msg = EmailMultiAlternatives('Thats your subject', html_content, 'from@yourdjangoapp.com', ['akarna772@gmail.com'], reply_to=[user.email])
        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'
        fp = open(img_url, 'rb')
        image = MIMEImage(fp.read())
        image.add_header('Content-ID', '<{}>'.format("qr_code"))
        msg.attach(image)
        msg.send()
        return Response({}, status=status.HTTP_200_OK)
        # send_mail(
        #     'Thats your subject',
        #     None,
        #     'from@yourdjangoapp.com',
        #     [user.email],
        #     html_message=html_content
        # )


class TOTPVerifyView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, token, format=None):
        user = request.user
        device = get_user_totp_device(self, user)
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            return Response(True, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)