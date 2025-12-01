#!/usr/bin/env python3
import os
import argparse
import requests
import feedparser

def download_file(url, output_path):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def main():
    parser = argparse.ArgumentParser(
        description="Télécharge les épisodes d'un flux RSS et les renomme 0.mp3, 1.mp3..."
    )

    parser.add_argument("rss", help="URL ou fichier RSS")
    parser.add_argument("-o", "--output", default="episodes", help="Dossier de sortie")
    parser.add_argument("-e", "--ext", default=None,
                        help="Extension forcée (ex: mp3). Par défaut : détectée automatiquement.")
    parser.add_argument("-n", "--max", type=int, default=None,
                        help="Nombre maximum d'épisodes à télécharger")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(f"📡 Lecture du flux RSS : {args.rss}")
    feed = feedparser.parse(args.rss)

    if not feed.entries:
        print("❌ Aucun épisode trouvé. Vérifie le RSS.")
        return

    max_dl = args.max if args.max is not None else len(feed.entries)
    print(f"➡️  Téléchargement des {max_dl} premiers épisodes")

    for idx, entry in enumerate(feed.entries[:max_dl]):
        if not entry.get("enclosures"):
            print(f"⚠️ Pas d'enclosure pour l'épisode {idx}, ignoré.")
            continue

        audio_url = entry.enclosures[0].href

        if args.ext:
            ext = args.ext
        else:
            ext = audio_url.split("?")[0].split(".")[-1]

        output_file = os.path.join(args.output, f"{idx}.{ext}")

        print(f"⬇️  Épisode {idx} → {output_file}")
        download_file(audio_url, output_file)

    print("✅ Téléchargement terminé.")

if __name__ == "__main__":
    main()
