#!/bin/sh
# Construit et sert localement le site Boîte Blanche pour prévisualiser la branche.
# Compatible macOS et Linux ; aucune action GitHub ni publication distante.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
DIST="$ROOT/dist"
PORT=${PREVIEW_PORT:-8000}
HOST=127.0.0.1
URL="http://$HOST:$PORT/"
SERVER_PID=
SERVER_LOG=$(mktemp "${TMPDIR:-/tmp}/boiteblanche-preview.XXXXXX")

cleanup() {
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    rm -f "$SERVER_LOG"
}
trap cleanup 0
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

if ! command -v python3 >/dev/null 2>&1; then
    echo "Erreur : Python 3 est requis. Installez Python 3 puis relancez ce script." >&2
    exit 1
fi

case "$PORT" in
    ''|*[!0-9]*)
        echo "Erreur : PREVIEW_PORT doit être un numéro de port (par défaut : 8000)." >&2
        exit 1
        ;;
esac
if [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "Erreur : PREVIEW_PORT doit être compris entre 1 et 65535." >&2
    exit 1
fi

echo "==> Construction du site complet…"
python3 "$ROOT/scripts/build_site.py"

echo "==> Vérification du manifeste PWA et des ressources hors ligne…"
python3 "$ROOT/scripts/validate_site.py" "$DIST"

if command -v node >/dev/null 2>&1; then
    echo "==> Vérification de la syntaxe JavaScript…"
    node --check "$DIST/sw.js"
    node --check "$DIST/vendor/chart.js/chart.umd.min.js"
else
    echo "Information : Node.js absent ; vérification JavaScript ignorée."
fi

if ! python3 -c 'import socket,sys; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); r=s.connect_ex((sys.argv[1],int(sys.argv[2]))); s.close(); sys.exit(1 if r == 0 else 0)' "$HOST" "$PORT"; then
    echo "Erreur : le port $PORT est déjà utilisé. Choisissez un autre port avec PREVIEW_PORT." >&2
    exit 1
fi

echo "==> Démarrage du serveur local sur $URL"
python3 -u -m http.server "$PORT" --bind "$HOST" --directory "$DIST" >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

# Attendre que le serveur réponde, ou détecter rapidement un port déjà occupé.
attempt=0
while [ "$attempt" -lt 30 ]; do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        cat "$SERVER_LOG" >&2
        echo "Erreur : impossible de démarrer le serveur local (port $PORT ?)." >&2
        exit 1
    fi
    if python3 -c 'import socket,sys; s=socket.socket(); s.settimeout(.2); r=s.connect_ex((sys.argv[1],int(sys.argv[2]))); s.close(); sys.exit(0 if r == 0 else 1)' "$HOST" "$PORT"; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ "$attempt" -eq 30 ]; then
    echo "Erreur : le serveur ne répond pas sur $URL" >&2
    exit 1
fi

echo
echo "Prévisualisation prête : $URL"
echo "Le contenu servi provient de la branche actuellement présente dans ce checkout."
echo "Aucun fichier n'est envoyé à GitHub ni à un hébergeur distant."
echo "Pour arrêter le serveur et terminer le script : Ctrl+C."
echo

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 &
elif command -v gio >/dev/null 2>&1; then
    gio open "$URL" >/dev/null 2>&1 &
else
    echo "Ouvrez cette adresse dans votre navigateur : $URL"
fi

wait "$SERVER_PID"
