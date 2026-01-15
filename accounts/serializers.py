from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.ReadOnlyField()
    tokens = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'password', 'tokens']
        
    def validate_email(self, value):
        return value.lower()
    
    def validate_password(self, pwd):
        validate_password(pwd)
        return pwd
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def get_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
       
 
class LoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    

class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user', 'created_at']
        
    def validate(self, attributes):
        """
        Ensure only one default address per user
        """
        request = self.context.get("request")
        user = request.user if request else None

        is_default = attributes.get("is_default", False)

        if is_default and user:
            queryset = Address.objects.filter(user=user, is_default=True)

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"is_default": "You already have a default address."}
                )

        return attributes
    

class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'phone', 'street_address', 'city', 'state', 'country', 'is_default', 'created_at']