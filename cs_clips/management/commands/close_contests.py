from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg
from cs_clips.models import Contest, Video
from cs_clips.utils.desempate import desempate_ponderato

class Command(BaseCommand):
    help = 'Closes all open contests that have passed their end date and selects a winner.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        contests_to_close = Contest.objects.filter(
            end_date__lt=today,
            is_closed=False
        )
        if not contests_to_close.exists():
            self.stdout.write(self.style.SUCCESS('No contests to close.'))
            return
        for contest in contests_to_close:
            self.stdout.write(f'Closing contest: {contest.name}')
            videos = (
                Video.objects
                .filter(contest=contest)
                .annotate(avg_rating=Avg('ratings__value'))
            )
            if not videos.exists():
                self.stdout.write(self.style.WARNING(f'No videos found for contest {contest.name}. Closing without a winner.'))
                contest.is_closed = True
                contest.closed_at = timezone.now()
                contest.save()
                continue
            avg_rated_videos = [v for v in videos if v.avg_rating is not None]
            if avg_rated_videos:
                max_rating = max(v.avg_rating for v in avg_rated_videos)
                top_videos = [v for v in avg_rated_videos if v.avg_rating == max_rating]
            else:
                if videos.count() == 1:
                    winner = videos.first()
                    top_videos = [winner]
                else:
                    top_videos = list(videos)
            winner = top_videos[0] if len(top_videos) == 1 else desempate_ponderato(top_videos)
            contest.winner = winner
            contest.is_closed = True
            contest.closed_at = timezone.now()
            contest.save()
            self.stdout.write(self.style.SUCCESS(f'Contest {contest.name} closed. Winner: {winner.title}'))
