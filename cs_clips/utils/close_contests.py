from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg

from cs_clips.models import Contest, Video
from cs_clips.utils.desempate import desempate_ponderato


class Command(BaseCommand):
    help = "Closes all open contests and determines the weekly winner."

    def handle(self, *args, **options):
        today = timezone.now().date()

        # The job is expected to run on Saturday (weekday == 5)
        if today.weekday() != 5:
            self.stdout.write(
                self.style.WARNING(
                    f"Today is {today.strftime('%A')} − this task is intended to be executed on Saturday."
                )
            )

        open_contests = Contest.objects.filter(
            is_closed=False,
            start_date__lte=today,
            end_date__gte=today,
        )

        if not open_contests.exists():
            self.stdout.write(self.style.WARNING("No open contests found."))
            return

        for contest in open_contests:
            self.stdout.write(f"Processing contest #{contest.id} − {contest.name}…")

            videos = (
                Video.objects
                .filter(contest=contest)
                .annotate(avg_rating=Avg('ratings__value'))
            )

            if not videos.exists():
                # No videos uploaded – close the contest without a winner.
                contest.is_closed = True
                contest.closed_at = timezone.now()
                contest.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"Closed contest #{contest.id} with no videos uploaded."
                    )
                )
                continue

            avg_rated_videos = [v for v in videos if v.avg_rating is not None]

            if avg_rated_videos:
                max_rating = max(v.avg_rating for v in avg_rated_videos)
                top_videos = [v for v in avg_rated_videos if v.avg_rating == max_rating]
            else:
                # If every video has null average rating, fall back to view/comment based tie-break.
                top_videos = list(videos)

            # Decide winner (straight or tie-break).
            winner = (
                top_videos[0]
                if len(top_videos) == 1
                else desempate_ponderato(top_videos)
            )

            # Persist winner & close contest.
            contest.winner = winner
            contest.is_closed = True
            contest.closed_at = timezone.now()
            contest.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Contest #{contest.id} closed. Winner video id: {winner.id if winner else 'N/A'}"
                )
            ) 