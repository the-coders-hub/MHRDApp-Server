from rest_framework import viewsets
from .serializers import SignUpWriteSerializer, RegistrationSerializer, LoginSerializer
from .models import SignUpCode, UserToken, EmailDomain
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail


class AccountViewset(viewsets.GenericViewSet):
    queryset = SignUpCode.objects.all()
    serializer_class = SignUpWriteSerializer

    @classmethod
    def send_verification_email(cls, to_email, code):
        subject = 'Verify your account for MHRD Applicaiton'
        message = """
        To verify your account, copy paste the following code into verification panel.

        %s

        If you got this mail by error, please ignore it!
        """ % code
        send_mail(subject, message, 'no-reply@mhrdapp.com', [to_email])

    @list_route(methods=['POST'])
    def register(self, request):
        serialized_email = SignUpWriteSerializer(data=request.data)
        if serialized_email.is_valid():
            email = serialized_email.validated_data['email']
            if not EmailDomain.verify_domain(email):
                return Response({'success': False, 'message': 'Unrecognized email domain'}, status=HTTP_400_BAD_REQUEST)

            signup_code = SignUpCode.objects.all().filter(email=email).order_by('-timestamp')
            created = False
            if signup_code.exists():
                signup_code = signup_code[0]
            else:
                signup_code = SignUpCode.objects.create(email=email)
                created = True

            if signup_code.verified:
                return Response({'success': False, 'message': 'Email already registered'}, status=HTTP_400_BAD_REQUEST)
            if created:
                self.send_verification_email(email, signup_code.code)
                return Response({'success': True, 'message': 'Email sent with verification code'})
            return Response(
                {'success': False, 'message': 'Email verification request already sent'},
                status=HTTP_400_BAD_REQUEST)
        else:
            return Response(serialized_email.errors, status=HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'])
    def resend(self, request):
        serialized_email = SignUpWriteSerializer(data=request.data)
        if serialized_email.is_valid():
            email = serialized_email.validated_data['email']
            if not EmailDomain.verify_domain(email):
                return Response({'success': False, 'message': 'Unrecognized email domain'}, status=HTTP_400_BAD_REQUEST)

            old_verified = SignUpCode.objects.all().filter(email=email, verified=True)
            if old_verified.exists():
                return Response({'success': False, 'message': 'Email already registered'}, status=HTTP_400_BAD_REQUEST)

            # Mark old codes as marked as inactive
            SignUpCode.objects.all().filter(email=email).update(active=False)
            signup_code = SignUpCode.objects.create(email=email)

            self.send_verification_email(email, signup_code.code)
            return Response({'success': True, 'message': 'Email sent with verification code'})
        else:
            return Response(serialized_email.errors, status=HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'], serializer_class=RegistrationSerializer)
    def create_account(self, request):
        serialized_data = RegistrationSerializer(data=request.data)
        if serialized_data.is_valid():
            email = serialized_data.validated_data['email']
            code = serialized_data.validated_data['code']

            signup_code = SignUpCode.objects.all().filter(email=email, code=code, active=True, verified=False)
            if signup_code.exists():
                signup_code = signup_code[0]
                signup_code.verified = True
                signup_code.save()
            else:
                return Response({'success': False, 'message': 'Invalid code or email'}, status=HTTP_400_BAD_REQUEST)

            username = serialized_data.validated_data['username']
            password = serialized_data.validated_data['password']
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            usertoken = UserToken.objects.create(user=user)
            return Response(
                {
                    'success': True,
                    'token': usertoken.token.hex,
                },
            )
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'], serializer_class=LoginSerializer)
    def login(self, request):
        serialized_data = LoginSerializer(data=request.data)
        if serialized_data.is_valid():
            username = serialized_data.validated_data['username']
            password = serialized_data.validated_data['password']

            user = authenticate(username=username, password=password)
            if not user:
                return Response({'success': False, 'error': 'Invalid username/password'}, status=HTTP_400_BAD_REQUEST)
            else:
                usertoken = UserToken.objects.create(user=user)
                return Response(
                    {
                        'success': True,
                        'token': usertoken.token.hex
                    }
                )
        return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)
