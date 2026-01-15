# permissions.py

from rest_framework.permissions import BasePermission

class IsAgenceUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.agence
    
class IsChefAgence(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_chef_agence
    
class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff
