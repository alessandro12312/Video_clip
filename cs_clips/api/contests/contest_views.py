from django.forms import ValidationError
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Avg
from cs_clips.models import Contest, Video
from cs_clips.api.videos.video_serializers import VideoSerializer
from cs_clips.permissions import OnlyAdminsPermission
from cs_clips.utils.desempate import desempate_ponderato



class EndContestView(APIView):
    """
    Endpoint per chiudere il contest attivo associato a un tag e decretare il vincitore (con spareggio ponderato).
    """
    permission_classes = [OnlyAdminsPermission]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tag',
                description='Tag del contest da chiudere',
                required=True,
                type=str,
                enum=[choice[0] for choice in Contest.Tag.choices]  # Enum dinamico!
            )
        ]
    )
    def post(self, request):
        valid_tags = [choice[0] for choice in Contest.Tag.choices]
        tag = request.data.get("tag")

        if tag not in valid_tags:
            raise ValidationError({
                "tag": f"Valore non valido. Valori ammessi: {', '.join(valid_tags)}"
            })

        today = timezone.now().date()

        # Trova il contest attivo con il tag specificato
        contest = Contest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_closed=False,
            tag=tag
        ).first()

        if not contest:
            return Response({"detail": f"Nessun contest attivo per il tag '{tag}'."}, status=status.HTTP_404_NOT_FOUND)

        videos = (
            Video.objects
            .filter(contest=contest)
            .annotate(avg_rating=Avg('ratings__value'))
        )

        if not videos.exists():
            return Response({"detail": "Nessun video presente per questo contest."}, status=status.HTTP_404_NOT_FOUND)

        # Filtra i video che hanno una media voto valida (non null)
        avg_rated_videos = [v for v in videos if v.avg_rating is not None]

        if avg_rated_videos:
            # Trova la media voto massima
            max_rating = max(v.avg_rating for v in avg_rated_videos)
            # Prendi tutti i video a pari merito
            top_videos = [v for v in avg_rated_videos if v.avg_rating == max_rating]
        else:
            if videos.count() == 1:
                # Se c'è un solo video, è il vincitore anche senza voti
                winner = videos.first()
                top_videos = [winner]
            else:
                # Spareggio senza rating: usa views + commenti
                top_videos = list(videos)

        # Determina il vincitore (direttamente o con spareggio)
        winner = top_videos[0] if len(top_videos) == 1 else desempate_ponderato(top_videos)

        # Salva vincitore e chiudi il contest
        contest.winner = winner
        contest.is_closed = True
        closed_at_now = contest.closed_at = timezone.now()
        contest.save()

        winner_data = VideoSerializer(winner).data if winner else None

        # Se c'è stato spareggio, mostra anche la lista dei finalisti
        finalists_data = [VideoSerializer(v).data for v in top_videos] if len(top_videos) > 1 else None

        return Response({
            "contest": {
                "id": contest.id,
                "name": contest.name,
                "start_date": contest.start_date,
                "end_date": contest.end_date,
                "closed_at": closed_at_now,
                "winner_id": contest.winner.id if contest.winner else None
            },
            "winner": winner_data,
            "finalists": finalists_data
        }, status=status.HTTP_200_OK)


class ContestWinnersView(APIView):
    """
    Restituisce una lista paginata dei video vincitori
    dei contest passati (chiusi), ordinati dal contest più recente.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='page', type=int, required=False, description='Numero della pagina'),
            OpenApiParameter(name='page_size', type=int, required=False, description='Numero di risultati per pagina')
        ]
    )
    def get(self, request):
        # Prendi tutti i contest chiusi, con winner non null,
        # ordinati dal più recente
        contests = Contest.objects.filter(is_closed=True, winner__isnull=False).order_by('-closed_at')
        
        # Estraggo solo i video vincitori
        winners = [contest.winner for contest in contests if contest.winner is not None]

        # Applica la paginazione con il page_size globale
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(winners, request)

        # Serializzo la lista dei vincitori
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)