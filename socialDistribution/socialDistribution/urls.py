"""socialDistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from project.views import CheckUsernameView

urlpatterns = [
    path('', include('project.urls')),
    path('api/local/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/local/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/local/check-username/", CheckUsernameView.as_view(), name="check-username"),
    path('admin/', admin.site.urls),
    path("", include("django.contrib.auth.urls")),


] + static('assets/', document_root=settings.FRONTEND_ASSETS)
