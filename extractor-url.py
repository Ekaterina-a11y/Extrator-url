import sys
import re
from urllib.parse import urlparse
from collections import Counter

def normaliser_domaine(nom_domaine):
    """Normalise le nom de domaine en minuscules et supprime www."""
    nom_domaine = nom_domaine.lower()
    if nom_domaine.startswith('www.'):
        nom_domaine = nom_domaine[4:]
    return nom_domaine

def est_domaine_valide(nom_domaine):
    """Vérifie si le domaine a un format valide."""
    pattern = r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$'
    return re.match(pattern, nom_domaine) is not None

def extraire_domaines_avance(url):
    """Extrait et valide le domaine avec plus de précision."""
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        
        domaine_normalise = normaliser_domaine(parsed.netloc)
        
        # Vérification de la validité du domaine
        if not est_domaine_valide(domaine_normalise):
            return None
            
        return f"{parsed.scheme}://{domaine_normalise}" if parsed.scheme else f"https://{domaine_normalise}"
    
    except Exception as e:
        print(f"Erreur lors du traitement de l'URL {url}: {e}")
        return None

def main():
    # Vérifie qu'un fichier est passé en argument
    if len(sys.argv) < 2:
        print("Usage: python extractor-url.py <fichier_urls>")
        print("Options supplémentaires:")
        print("  --stats          Affiche des statistiques détaillées")
        print("  --no-protocol    Exclut le protocole dans la sortie")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "domaines.txt"
    
    # Options
    afficher_stats = "--stats" in sys.argv
    exclure_protocole = "--no-protocol" in sys.argv

    # Domaines à exclure (liste élargie)
    domaines_exclus = {
        "free.fr", "google", "facebook", "twitter", "linkedin", 
        "youtube", "instagram", "wikipedia", "github", "bit.ly",
        "t.co", "goo.gl", "amazon", "microsoft", "apple"
    }

    # Domaines de réseaux sociaux courants
    reseaux_sociaux = {
        "facebook.com", "twitter.com", "linkedin.com", "instagram.com",
        "youtube.com", "tiktok.com", "pinterest.com", "reddit.com"
    }

    # Compteurs pour les statistiques
    stats = {
        'total_urls': 0,
        'urls_valides': 0,
        'domaines_uniques': 0,
        'reseaux_sociaux': 0,
        'domaines_exclus': 0
    }

    domaines = set()
    tous_domaines = []  # Pour les statistiques

    try:
        # Lecture du fichier d'entrée
        with open(input_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                url = line.strip()
                stats['total_urls'] += 1
                
                if not url:
                    continue

                domaine_complet = extraire_domaines_avance(url)
                if not domaine_complet:
                    continue

                # Extraire le nom de domaine sans protocole pour les vérifications
                nom_domaine = urlparse(domaine_complet).netloc

                # Vérifier l'exclusion
                exclure = any(dom_exclu in nom_domaine for dom_exclu in domaines_exclus)
                if exclure:
                    stats['domaines_exclus'] += 1
                    continue

                # Compter les réseaux sociaux
                if any(reseau in nom_domaine for reseau in reseaux_sociaux):
                    stats['reseaux_sociaux'] += 1

                # Formater la sortie selon l'option
                if exclure_protocole:
                    sortie_domaine = nom_domaine
                else:
                    sortie_domaine = domaine_complet

                if sortie_domaine not in domaines:
                    domaines.add(sortie_domaine)
                    tous_domaines.append(nom_domaine)
                    stats['urls_valides'] += 1

        stats['domaines_uniques'] = len(domaines)

        # Écriture du fichier de sortie
        with open(output_file, "w", encoding="utf-8") as f:
            for domaine in sorted(domaines):
                f.write(domaine + "\n")

        # Affichage des résultats
        print(f"✅ {stats['domaines_uniques']} domaines uniques enregistrés dans {output_file}")
        
        if afficher_stats:
            print("\n📊 STATISTIQUES DÉTAILLÉES:")
            print(f"   URLs totales lues: {stats['total_urls']}")
            print(f"   URLs valides traitées: {stats['urls_valides']}")
            print(f"   Domaines exclus: {stats['domaines_exclus']}")
            print(f"   Réseaux sociaux détectés: {stats['reseaux_sociaux']}")
            
            # Top 10 des domaines les plus fréquents
            if tous_domaines:
                compteur = Counter(tous_domaines)
                print(f"\n🏆 TOP 10 des domaines:")
                for domaine, count in compteur.most_common(10):
                    print(f"   {domaine}: {count} occurrence(s)")

    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{input_file}' n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()