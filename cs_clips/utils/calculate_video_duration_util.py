# tasks.py
import os
import tempfile
from celery import shared_task
from moviepy import VideoFileClip
from cs_clips.models import Video

@shared_task
def calculate_video_duration_task(video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return f"Video with id {video_id} not found."

    tmp_file_path = None
    try:
        # Scarica il file da MinIO in un file temporaneo
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            for chunk in video.file.chunks():
                tmp.write(chunk)
            tmp_file_path = tmp.name

        # Calcola la durata
        with VideoFileClip(tmp_file_path) as clip:
            video.duration = int(clip.duration)
            video.save(update_fields=["duration"])

        return f"Duration for video {video_id} set to {video.duration}."

    except Exception as e:
        # Gestisci l'errore (es. loggalo)
        # Potresti voler implementare dei tentativi (retries)
        video.delete() # Opzionale: cancella se il calcolo fallisce
        raise e
    finally:
        # Pulisci sempre il file temporaneo
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)