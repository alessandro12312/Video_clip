#!/usr/bin/env sh
set -e

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ▶️ Inizio script di init dinamico"

# 1. Alias “local” per MinIO
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📌 Imposto alias “local”..."
mc alias set local http://minio:9000 \
    "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Alias impostato correttamente"

# 2. Creazione console user
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📌 Aggiungo console user “${MINIO_ACCESS_KEY}”..."
mc admin user add local \
    "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Utente creato correttamente"

# 3. Creazione policy admin
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📌 Creo policy “${MINIO_ACCESS_KEY}Admin”..."
mc admin policy create local \
    "${MINIO_ACCESS_KEY}Admin" /policy/admin.json
echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Policy creata correttamente"

# 4. Associazione policy all’utente
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📌 Associo policy a utente “${MINIO_ACCESS_KEY}”..."
mc admin policy attach local \
    "${MINIO_ACCESS_KEY}Admin" --user="${MINIO_ACCESS_KEY}"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Policy associata correttamente"

# 5. Creazione dinamica di tutti i bucket definiti in .env
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📌 Creazione dinamica dei bucket dall’ambiente..."
for entry in $(env); do
  case "$entry" in
    MINIO_STORAGE_*_BUCKET=*)
      # estraggo il valore grezzo
      raw="${entry#*=}"
      # rimuovo eventuali CR (\r) e virgolette residue
      clean="$(printf '%s' "$raw" | tr -d '\r' | tr -d '"')"
      # trim spazi iniziali
      while [ "${clean# }" != "$clean" ]; do
        clean="${clean# }"
      done
      # trim spazi finali
      while [ "${clean% }" != "$clean" ]; do
        clean="${clean% }"
      done

      echo "  • Rilevata variabile $entry → bucket “$clean”"
      mc mb --ignore-existing local/"$clean"
      echo "  ✅ Bucket “$clean” pronto (o già esistente)"
      ;;
  esac
done

echo "[$(date +'%Y-%m-%d %H:%M:%S')] 🎉 Init completato con successo"
