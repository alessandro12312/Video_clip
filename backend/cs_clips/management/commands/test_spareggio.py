from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cs_clips.models import Contest, Video, Rating, Comment
from cs_clips.utils.desempate import desempate_ponderato
from cs_clips.serializers import VideoSerializer
from django.utils import timezone
import tempfile

User = get_user_model()

class Command(BaseCommand):
    help = "Crea dati di test per la normalizzazione dello spareggio tra due video."

    def handle(self, *args, **options):
        # Pulizia dati per evitare duplicati tra esecuzioni
        User.objects.all().delete()
        Video.objects.all().delete()
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Contest.objects.all().delete()

        # 1. Creazione utenti
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        user3 = User.objects.create_user(username='user3', password='pass')

        # 2. Contest settimanale attivo
        today = timezone.now().date()
        contest = Contest.objects.create(
            name='Contest Test',
            start_date=today,
            end_date=today,
            is_closed=False
        )

        # 3. Crea file fittizi per i video
        temp_file1 = tempfile.NamedTemporaryFile(suffix=".mp4")
        temp_file2 = tempfile.NamedTemporaryFile(suffix=".mp4")

        # 4. Crea due video
        video1 = Video.objects.create(
            title="Video Uno",
            uploader=user1,
            contest=contest,
            file=temp_file1.name
        )
        video2 = Video.objects.create(
            title="Video Due",
            uploader=user2,
            contest=contest,
            file=temp_file2.name
        )

        # 5. Voti (media uguale: 7.5)
        # Video1: 7, 8
        Rating.objects.create(user=user1, video=video1, value=7)
        Rating.objects.create(user=user2, video=video1, value=8)
        # Video2: 8, 7
        Rating.objects.create(user=user1, video=video2, value=8)
        Rating.objects.create(user=user3, video=video2, value=7)

        # 6. Commenti (più commenti su video2)
        Comment.objects.create(user=user1, video=video1, content="Bravo!")
        Comment.objects.create(user=user2, video=video1, content="Bello!")
        # Video2 riceve più commenti
        Comment.objects.create(user=user1, video=video2, content="Top!")
        Comment.objects.create(user=user2, video=video2, content="Mi piace molto")
        Comment.objects.create(user=user3, video=video2, content="sega a pedali")

        # 7. Visualizzazioni (manualmente, per test)
        video1.views = 10
        video2.views = 30  # più visualizzazioni su video2
        video1.save()
        video2.save()

        # 8. Raccolta dei video "finalisti" (simula spareggio)
        finalisti = [video1, video2]

        print("---- DATI DEI VIDEO FINALISTI ----")
        for v in finalisti:
            print(f"{v.title}: media voto={sum(r.value for r in v.ratings.all())/v.ratings.count():.2f}, "
                  f"n_voti={v.ratings.count()}, n_commenti={v.comments.count()}, views={v.views}")

        # Serializza tutti i finalisti
        finalists_serialized = [VideoSerializer(v).data for v in finalisti]
        print("\nDati serializzati dei finalisti (formato dict):")
        for v in finalists_serialized:
            print(v)

        # Stampa anche in formato JSON pretty
        import json
        print("\nDati serializzati dei finalisti (formato JSON pretty):")
        print(json.dumps(finalists_serialized, indent=2, ensure_ascii=False))

        # 9. Applica algoritmo di spareggio ponderato
        vincitore = desempate_ponderato(finalisti)
        print("\n***** VIDEO VINCITORE SECONDO L'ALGORITMO *****")
        print(f"{vincitore.title}\n")
        print("Dati serializzati del vincitore:")
        print(VideoSerializer(vincitore).data)

        self.stdout.write(self.style.SUCCESS(f"Vincitore: {vincitore.title}"))
