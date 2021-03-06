"""RUF_assassins URL Configuration

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
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from start_page.views import rules, home
from login.views import signup, login, logout, verify_pin, upload_image, game_admin
from target.views import target, kill_report, stats, confirm_kill_page, confirm_kill_agree, confirm_kill_deny, leaderboard, kill_feed

urlpatterns = [
    path('home/', home, name="home"),
    path('rules/', rules, name="rules"),
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('verify/', verify_pin, name="verifypin"),
    path('profileimage/', upload_image, name="uploadimage"),
    path('target/', target, name="target"),
    path('killreport/',kill_report, name="killreport"),
    path('stats/',stats,name="stats"),
    path('confirmkill', confirm_kill_page, name="confirmkill"),
    path('confirm', confirm_kill_agree, name="confirm"),
    path('deny', confirm_kill_deny, name="deny"),
    path('admin/', admin.site.urls),
    path('gameadmin/', game_admin, name="gameadmin"),
    path('leaderboard',leaderboard, name="leaderboard"),
    path('killfeed',kill_feed, name="killfeed"),
    path('', home, name="homepage"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
