# cs_clips/management/commands/debug_storage.py
"""
Django Management Command per testare il file storage
Equivale a un @Component con CommandLineRunner in Spring Boot
"""

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import tempfile
import os

class Command(BaseCommand):
    help = 'Debug del sistema di storage per verificare MinIO'
    
    def handle(self, *args, **options):
        """
        Equivale al main() di un CommandLineRunner in Spring Boot
        """
        self.stdout.write("🔍 Debug Django File Storage")
        self.stdout.write("=" * 50)
        
        # 1. Verifica configurazione settings
        self.debug_settings()
        
        # 2. Verifica il storage backend effettivo
        self.debug_storage_backend()
        
        # 3. Test upload diretto
        self.test_direct_upload()
        
        # 4. Test come farebbe il serializer
        self.test_serializer_like_upload()
    
    def debug_settings(self):
        """Verifica le impostazioni Django - come @ConfigurationProperties"""
        self.stdout.write("\n📋 Configurazione Settings:")
        
        storage_settings = [
            'DEFAULT_FILE_STORAGE',
            'AWS_ACCESS_KEY_ID', 
            'AWS_SECRET_ACCESS_KEY',
            'AWS_STORAGE_BUCKET_NAME',
            'AWS_S3_ENDPOINT_URL',
            'MEDIA_URL',
            'MEDIA_ROOT'
        ]
        
        for setting in storage_settings:
            value = getattr(settings, setting, 'NON DEFINITO')
            self.stdout.write(f"  {setting}: {value}")
    
    def debug_storage_backend(self):
        """Verifica quale backend storage sta usando Django"""
        self.stdout.write(f"\n🔧 Storage Backend Attivo:")
        self.stdout.write(f"  Tipo: {type(default_storage)}")
        self.stdout.write(f"  Classe: {default_storage.__class__.__name__}")
        
        # Verifica se è S3
        if hasattr(default_storage, 'bucket_name'):
            self.stdout.write(f"  Bucket: {default_storage.bucket_name}")
        if hasattr(default_storage, 'endpoint_url'):
            self.stdout.write(f"  Endpoint: {default_storage.endpoint_url}")
        if hasattr(default_storage, 'location'):
            self.stdout.write(f"  Location: {default_storage.location}")
    
    def test_direct_upload(self):
        """Test upload diretto usando default_storage"""
        self.stdout.write(f"\n⬆️ Test Upload Diretto:")
        
        try:
            # Crea un file di test
            test_content = b"Test file content from Django"
            test_file = ContentFile(test_content, name="test_django_upload.txt")
            
            # Salva usando default_storage (come fa Django internamente)
            file_path = default_storage.save("test/django_direct_test.txt", test_file)
            
            self.stdout.write(f"  ✅ File salvato in: {file_path}")
            
            # Verifica URL
            if default_storage.exists(file_path):
                file_url = default_storage.url(file_path)
                self.stdout.write(f"  🌐 URL: {file_url}")
                
                # Verifica se il file è su MinIO o filesystem locale
                if file_url.startswith('http://localhost:9000'):
                    self.stdout.write("  ✅ File caricato su MinIO!")
                else:
                    self.stdout.write("  ❌ File probabilmente su filesystem locale")
            
            # Cleanup
            default_storage.delete(file_path)
            self.stdout.write("  🧹 File di test rimosso")
            
        except Exception as e:
            self.stdout.write(f"  ❌ Errore: {e}")
    
    def test_serializer_like_upload(self):
        """Simula quello che fa il serializer con MoviePy"""
        self.stdout.write(f"\n🎬 Test Simulazione Serializer:")
        
        try:
            # Crea un file temporaneo come fa il serializer
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(b"Fake video content for testing")
                temp_file_path = temp_file.name
            
            # Simula la lettura del file come fa il serializer
            with open(temp_file_path, 'rb') as f:
                file_content = f.read()
                django_file = ContentFile(file_content, name="test_video.mp4")
            
            # Salva come farebbe il model
            saved_path = default_storage.save("videos/test_video.mp4", django_file)
            
            self.stdout.write(f"  📁 Path salvato: {saved_path}")
            
            if default_storage.exists(saved_path):
                url = default_storage.url(saved_path)
                self.stdout.write(f"  🌐 URL generata: {url}")
                
                # Verifica destinazione finale
                if 'localhost:9000' in url:
                    self.stdout.write("  ✅ Video salvato su MinIO!")
                else:
                    self.stdout.write("  ❌ Video salvato su filesystem locale")
                    
                    # Se è locale, mostra dove
                    if hasattr(default_storage, 'path'):
                        try:
                            local_path = default_storage.path(saved_path)
                            self.stdout.write(f"  📂 Path locale: {local_path}")
                        except:
                            pass
            
            # Cleanup
            default_storage.delete(saved_path)
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.stdout.write(f"  ❌ Errore simulazione: {e}")
            import traceback
            self.stdout.write(f"  🔍 Traceback: {traceback.format_exc()}")
    
    def add_arguments(self, parser):
        """Aggiunge opzioni al comando - come @Option in Spring Boot"""
        parser.add_argument(
            '--bucket-test',
            action='store_true',
            help='Esegue solo il test del bucket MinIO',
        )