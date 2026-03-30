import os
from pathlib import Path

# Percorso del file .env
env_file = Path(__file__).parent / '.env'

# Token fornito dall'utente
read_access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjNjc3YTBlZmY3NTMzYWM4Y2IyYmM4ZTU3MDVlOWFlNyIsIm5iZiI6MTc3NDgwNzAzNC42NzYsInN1YiI6IjY5Yzk2N2ZhMzNiODAyMDlkY2JiYjBiMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.-6xMzM690wXsa3a2SMsbSrcb4tjGWjQ0nxBlMxegYy0"

# Leggi il contenuto esistente del .env
if env_file.exists():
    with open(env_file, 'r') as f:
        content = f.read()
else:
    content = ""

# Rimuovi la vecchia linea TMDB_READ_ACCESS_TOKEN se esiste
lines = content.split('\n')
new_lines = []
token_added = False

for line in lines:
    if line.startswith('TMDB_READ_ACCESS_TOKEN='):
        if not token_added:
            new_lines.append(f'TMDB_READ_ACCESS_TOKEN={read_access_token}')
            token_added = True
    else:
        new_lines.append(line)

# Se non esisteva, aggiungilo alla fine
if not token_added:
    new_lines.append(f'TMDB_READ_ACCESS_TOKEN={read_access_token}')

# Scrivi il nuovo contenuto
with open(env_file, 'w') as f:
    f.write('\n'.join(new_lines))

print("TMDB Read Access Token aggiunto al file .env")
print("Riavvia il server Django per applicare le modifiche")
