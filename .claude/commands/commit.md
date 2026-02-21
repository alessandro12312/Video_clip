---
name: commit
description: 'Commit automatico con riepilogo dettagliato delle modifiche. Usa "* yolo" per committare tutto senza conferma.'
---

# Commit con riepilogo

Esegui un commit git con un messaggio dettagliato che riassume tutte le modifiche fatte.

## Istruzioni

1. Esegui `git status` e `git diff` (staged e unstaged) per analizzare tutte le modifiche correnti.

2. Analizza ogni file modificato e produci un messaggio di commit strutturato cosi':
   - Prima riga: titolo breve (max 72 caratteri) che riassume il tipo di modifica (fix, feat, refactor, docs, ecc.)
   - Riga vuota
   - Corpo: elenco puntato delle modifiche principali raggruppate per area/file
   - Footer con: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

3. Controlla gli argomenti passati: $ARGUMENTS

4. **Se gli argomenti contengono "* yolo" o "yolo"**:
   - Aggiungi TUTTI i file modificati e nuovi allo staging (`git add -A`)
   - Crea il commit direttamente SENZA chiedere conferma all'utente
   - NON committare file che contengono segreti (.env, credentials, chiavi API, ecc.) - escludili e avvisa

5. **Se gli argomenti NON contengono "yolo"**:
   - Mostra all'utente il riepilogo delle modifiche e il messaggio di commit proposto
   - Chiedi conferma prima di procedere
   - Se l'utente specifica file specifici (es. `/commit src/app.js`), aggiungi solo quei file

6. Dopo il commit, esegui `git status` per verificare che sia andato a buon fine e mostra il risultato.

7. NON fare `git push` a meno che l'utente non lo richieda esplicitamente.

IMPORTANTE: Passa sempre il messaggio di commit tramite HEREDOC per garantire la formattazione corretta:
```
git commit -m "$(cat <<'EOF'
Messaggio qui

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```
