import csv
import io
from django.utils import timezone
from api.models import (
    AssessmentCampaign,
    AssessmentAttempt,
    CandidateSelection,
    ReportExport,
    ExportType,
)

class ReportService:
    @staticmethod
    def generate_campaign_summary(campaign: AssessmentCampaign):
        """
        Generates executive analytics and rankings across all candidates in a campaign.
        """
        attempts = AssessmentAttempt.objects.filter(campaign=campaign).select_related('candidate', 'candidate__profile')
        total_candidates = attempts.values('candidate').distinct().count()
        passed_attempts = attempts.filter(passed=True).count()
        failed_attempts = attempts.filter(status='FAILED').count()

        # Build candidate leaderboards
        candidate_ranks = []
        for att in attempts.order_by('-final_score'):
            profile = getattr(att.candidate, 'candidate_profile', None)
            candidate_ranks.append({
                "candidate_id": att.candidate.id,
                "username": att.candidate.username,
                "email": att.candidate.email,
                "technical_track": profile.technical_track if profile else "general",
                "final_score": round(att.final_score, 2),
                "passed": att.passed,
                "status": att.status,
                "attempt_number": att.attempt_number,
                "submitted_at": att.submitted_at.isoformat() if att.submitted_at else None,
            })

        # Fetch existing selections (top 4 or designated)
        selections = CandidateSelection.objects.filter(campaign=campaign).select_related('candidate')
        selection_list = [
            {
                "candidate_id": sel.candidate.id,
                "username": sel.candidate.username,
                "ranking": sel.ranking,
                "decision": sel.decision,
                "notes": sel.notes,
            }
            for sel in selections
        ]

        return {
            "campaign_id": campaign.id,
            "campaign_title": campaign.title,
            "total_candidates": total_candidates,
            "passed_count": passed_attempts,
            "failed_count": failed_attempts,
            "candidates": candidate_ranks,
            "selections": selection_list,
        }

    @classmethod
    def export_report_csv(cls, campaign: AssessmentCampaign, requested_by):
        """
        Exports a CSV spreadsheet summarizing candidate scores and rankings.
        """
        summary = cls.generate_campaign_summary(campaign)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['Candidate ID', 'Username', 'Email', 'Track', 'Final Score', 'Passed', 'Status', 'Submitted At'])
        for c in summary['candidates']:
            writer.writerow([
                c['candidate_id'],
                c['username'],
                c['email'],
                c['technical_track'],
                c['final_score'],
                c['passed'],
                c['status'],
                c['submitted_at'] or 'In Progress'
            ])

        csv_content = output.getvalue()
        report = ReportExport.objects.create(
            campaign=campaign,
            requested_by=requested_by,
            export_type=ExportType.CSV,
            status='COMPLETED',
            result_data={"row_count": len(summary['candidates']), "csv_text": csv_content}
        )
        return report, csv_content
