from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (FireObjectView,
                    index,
                    object_create,
                    fireload_add,
                    update,
                    delete,
                    login_view,
                    logout_view,
                    fire_load_create,
                    fire_load_list,
                    fire_load_update,
                    fire_load_delete,)


app_name = 'rkp'

router = DefaultRouter()
router.register('rkp',
                FireObjectView,
                basename='rkp')

urlpatterns = [
    path('', index, name='index'),
    path('<int:pk>/update/', update, name='update'),
    path('<int:pk>/delete/', delete, name='delete'),
    path('object_create/', object_create, name='object_create'),
    path('<int:pk>/fire_load/', fireload_add, name='fireload_add'),
    path('fire_load_list/<int:pk>/update/',
         fire_load_update,
         name='fire_load_update'),
    path('fire_load_list/<int:pk>/delete/',
         fire_load_delete,
         name='fire_load_delete'),
    path('fire_load_list/', fire_load_list, name='fire_load_list'),
    path('fire_load_create/', fire_load_create, name='fire_load_create'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
