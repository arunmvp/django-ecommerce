from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings

from .serializers import register_user, user_serializer, ProductSerializer, CartItemSerializer , NewsletterSerializer
from .models import Product, CartItem , NewsletterSubscriber


@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({"message": "Welcome to E-commerce API!"})


# 🔹 Register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = register_user(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User registered successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Login
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# 🔹 Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = user_serializer(request.user)
    return Response(serializer.data)


# 🔹 Product APIs (ReadOnly)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# 🔹 Cart APIs
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    # 🛒 Add item to cart
    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    #  Update quantity
    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        quantity = int(request.data.get('quantity', 1))
        item = self.get_queryset().get(pk=pk)
        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)

    #  Remove from cart
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        item = self.get_queryset().get(pk=pk)
        item.delete()
        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

    #  Get cart total
    @action(detail=False, methods=['get'])
    def total(self, request):
        items = self.get_queryset()
        total_price = sum([i.subtotal for i in items])
        return Response({"total": total_price})



# 🔹 Newsletter Subscribe API
@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Already subscribed check
    if NewsletterSubscriber.objects.filter(email=email).exists():
        return Response({"message": "Already subscribed!"}, status=status.HTTP_200_OK)

    # Save subscriber
    subscriber = NewsletterSubscriber.objects.create(email=email)

    # Send confirmation email
    try:
        send_mail(
            subject="🎉 Thanks for Subscribing to our cake art! ",
            message="Hi! Thanks for subscribing to our newsletter. You'll receive fresh updates soon.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        return Response(
            {"message": f"Subscribed, but email failed to send: {str(e)}"},
            status=status.HTTP_201_CREATED,
        )

    serializer = NewsletterSerializer(subscriber)
    return Response(
        {"message": "Successfully subscribed & confirmation email sent!", "data": serializer.data},
        status=status.HTTP_201_CREATED,
    )