from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from core.models import File
from core.serializers import UserSerializer, FileSerializer
from .models import SignUpCode, UserToken, EmailDomain, UserProfile, Designation
from .serializers import (SignUpWriteSerializer, RegistrationSerializer, LoginSerializer,
                          UpdateProfileSerializer, FilteredDesignationSerializer, DesignationSerializer)


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
        """
        Register email for account creation
        ---
        response_serializer: core.serializers.SimpleResponseSerializer
        """
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
        """
        Resend verification code
        ---
        response_serializer: core.serializers.SimpleResponseSerializer
        """
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
        """
        Create account by verifying code
        ---
        request_serializer: account.serializers.RegistrationSerializer
        response_serializer: core.serializers.LoginResponseSerializer
        """
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
        """
        Login user with credentials
        ---
        request_serializer: account.serializers.LoginSerializer
        response_serializer: core.serializers.LoginResponseSerializer
        """
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


class UserViewset(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['POST'], serializer_class=UpdateProfileSerializer)
    def update_profile(self, request, pk):
        """
        For updating first_name, last_name, college
        ---
        request_serializer: account.serializers.UpdateProfileSerializer
        response_serializer: core.serializers.UserSerializer
        """
        user = get_object_or_404(User, pk=pk)
        if request.user.id != user.id:
            return Response({'success': False, 'message': 'Unauthorized request'}, status=HTTP_403_FORBIDDEN)

        serialized_data = UpdateProfileSerializer(instance=user.profile, data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            user.refresh_from_db()
            return Response(UserSerializer(user).data)
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    @detail_route(methods=['POST'], serializer_class=FileSerializer)
    def update_picture(self, request, pk):
        """
        Update profile picture
        ---
        request_serializer: core.serializers.FileSerializer
        response_serializer: core.serializers.UserSerializer
        parameters:
            - name: file
              type: file
              required: true
        """
        profile = get_object_or_404(UserProfile, user_id=pk)
        if request.user.id != profile.user.id:
            return Response({'success': False, 'message': 'Unauthorized request'}, status=HTTP_403_FORBIDDEN)
        picture = request.FILES.get('file', None)
        if not picture:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        file = File.objects.create(file=picture)
        profile.picture = file
        profile.save()
        return Response(UserSerializer(profile.user).data)

    @detail_route(methods=['POST'], serializer_class=FilteredDesignationSerializer)
    def add_designation(self, request, pk):
        """
        Add new designations
        ---
        request_serializer: account.serializers.FilteredDesignationSerializer
        response_serializer: core.serializers.UserSerializer
        """
        user = get_object_or_404(User, pk=pk)
        if request.user.id != user.id:
            return Response({'success': False, 'message': 'Unauthorized request'}, status=HTTP_403_FORBIDDEN)

        serialized_data = FilteredDesignationSerializer(data=request.data)
        if serialized_data.is_valid():
            designation = serialized_data.save()
            user.profile.designations.add(designation)
            return Response(UserSerializer(user).data)
        else:
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

    @detail_route(methods=['GET'])
    def get_designations(self, request, pk):
        """
        Get user designations.

        If requesting user is same as user requested, then return all designations.
        Else return only verified designations.
        ---
        response_serializer: account.serializers.DesignationSerializer
        """
        user = get_object_or_404(User, pk=pk)
        get_verified = True
        if request.user.id == user.id:
            get_verified = False

        designations = Designation.objects.filter(userprofile__user=user)
        if get_verified:
            designations = designations.filter(verified=True)
        return Response(DesignationSerializer(designations, many=True).data)

    @list_route()
    def current(self, request):
        """
        Get current user details
        ---
        response_serializer: core.serializers.UserSerializer
        """
        return Response(UserSerializer(request.user).data)
