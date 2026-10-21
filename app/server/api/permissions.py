from rest_framework import permissions
from .models import UserRole

def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserRole.ADMIN
    if hasattr(user, 'profile'):
        return user.profile.role
    return UserRole.CANDIDATE


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with the Administrator role or superusers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, 'profile') and request.user.profile.role == UserRole.ADMIN
        )


class IsReviewerRole(permissions.BasePermission):
    """
    Allows access to Reviewers and Admins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.role in (UserRole.REVIEWER, UserRole.ADMIN)
        return False


class IsCandidateRole(permissions.BasePermission):
    """
    Allows access to authenticated Candidates.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if hasattr(request.user, 'profile'):
            return request.user.profile.role == UserRole.CANDIDATE
        return True


class IsAttemptOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission: Candidates can only access their own attempts or submissions.
    Staff/Admins and assigned Reviewers have broader access.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == UserRole.ADMIN):
            return True

        # Candidate ownership check
        candidate_user = None
        if hasattr(obj, 'candidate'):
            candidate_user = obj.candidate
        elif hasattr(obj, 'assessment_attempt'):
            candidate_user = obj.assessment_attempt.candidate
        elif hasattr(obj, 'stage_attempt'):
            candidate_user = obj.stage_attempt.assessment_attempt.candidate
        elif hasattr(obj, 'user'):
            candidate_user = obj.user

        if candidate_user == request.user:
            return True

        # Check if user is an assigned reviewer
        if hasattr(request.user, 'profile') and request.user.profile.role == UserRole.REVIEWER:
            stage_attempt = None
            if hasattr(obj, 'stage_attempt'):
                stage_attempt = obj.stage_attempt
            elif hasattr(obj, 'assessment_attempt'):
                # Check any assigned review in this attempt
                return obj.stage_attempts.filter(reviewer_assignments__reviewer=request.user).exists()
            elif hasattr(obj, 'reviewer_assignments'):
                return obj.reviewer_assignments.filter(reviewer=request.user).exists()
            
            if stage_attempt:
                return stage_attempt.reviewer_assignments.filter(reviewer=request.user).exists()

        return False
