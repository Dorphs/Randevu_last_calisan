from rest_framework import permissions

class IsReportOwnerOrRecipient(permissions.BasePermission):
    """Rapor sahibi veya alıcısı için izinler"""
    
    def has_object_permission(self, request, view, obj):
        # GET, HEAD veya OPTIONS için izin ver
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.created_by == request.user or
                request.user in obj.recipients.all()
            )
        
        # Diğer metodlar için sadece sahibine izin ver
        return obj.created_by == request.user

class IsDashboardOwnerOrShared(permissions.BasePermission):
    """Dashboard sahibi veya paylaşılan kullanıcılar için izinler"""
    
    def has_object_permission(self, request, view, obj):
        # Eğer dashboard public ise ve güvenli metod ise izin ver
        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True
            
        # GET, HEAD veya OPTIONS için izin ver
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.owner == request.user or
                request.user in obj.shared_with.all()
            )
        
        # Diğer metodlar için sadece sahibine izin ver
        return obj.owner == request.user

class IsWidgetDashboardOwnerOrShared(permissions.BasePermission):
    """Widget'ın bağlı olduğu dashboard'un sahibi veya paylaşılan kullanıcılar için izinler"""
    
    def has_object_permission(self, request, view, obj):
        dashboard = obj.dashboard
        
        # Eğer dashboard public ise ve güvenli metod ise izin ver
        if dashboard.is_public and request.method in permissions.SAFE_METHODS:
            return True
            
        # GET, HEAD veya OPTIONS için izin ver
        if request.method in permissions.SAFE_METHODS:
            return (
                dashboard.owner == request.user or
                request.user in dashboard.shared_with.all()
            )
        
        # Diğer metodlar için sadece dashboard sahibine izin ver
        return dashboard.owner == request.user
