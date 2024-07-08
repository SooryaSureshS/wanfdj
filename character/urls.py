# noinspection GrazieInspection
""" WAMFO URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.conf import settings
from character.views import Characters, CharactersList, CharactersForm
from character.views import OwnedCharacter, NotOwnedCharacter, CurrentCharacter
from character.views import Armors, ArmorsList, ArmorsForm, StudentAllCharacters
from character.views import Tools, ToolsList, ToolsForm, StudentCharacterTool, StudentCharacterArmor

urlpatterns = [
    # Admin
    path('character/', Characters.as_view(), name='Characters'),
    path('character/list', CharactersList.as_view(), name='Characters List'),
    path('character/form', CharactersForm.as_view(), name='Characters Form'),
    path('armor', Armors.as_view(), name='Armors'),
    path('armor/list', ArmorsList.as_view(), name='Armors List'),
    path('armor/form', ArmorsForm.as_view(), name='Armors Form'),
    path('tool/', Tools.as_view(), name='Tools'),
    path('tool/list', ToolsList.as_view(), name='Tools List'),
    path('tool/form', ToolsForm.as_view(), name='Tools Form'),

    # Student
    path('student/owned/character', OwnedCharacter.as_view(), name='Owned Characters'),
    path('student/user/character/group', StudentAllCharacters.as_view(), name='Owned Characters By group'),
    # path('student/other/character', NotOwnedCharacter.as_view(), name='Characters'),
    path('student/current/character', CurrentCharacter.as_view(), name='Current Character'),
    path('student/character/tool', StudentCharacterTool.as_view(), name='Current Character Tool'),
    path('student/character/armor', StudentCharacterArmor.as_view(), name='Current Character Armor'),

    # All
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
