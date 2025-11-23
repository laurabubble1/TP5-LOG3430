import os
import re
from typing import Optional, Dict, Iterable, Tuple

# Regex correspond aux deux formes :
# [timestamp][LEVEL][username] action
# [timestamp][LEVEL] action            (messages système / serveur sans nom d'utilisateur)
LOG_PATTERN = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\[(?P<level>[^\]]+)\](?:\[(?P<username>[^\]]+)\])?\s*(?P<action>.*)$")

def parse_log_line(line: str) -> Optional[Dict[str, str]]:
    """Analyse une seule ligne de log et extrait timestamp, niveau, nom d'utilisateur optionnel et action.

    Retourne None lorsque la ligne ne correspond pas au format attendu.
    """
    line = line.strip()
    if not line or not line.startswith('['):
        return None
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()
    data['action'] = data['action'].strip()
    if not data.get('username'):
        data['username'] = 'system'
    return data

def _iter_decoded_lines(path: str) -> Iterable[str]:
    """Génère les lignes décodées d'un fichier de log, gérant automatiquement les encodages BOM courants."""
    with open(path, 'rb') as raw:
        data = raw.read()
    # Détection du BOM
    if data.startswith(b'\xff\xfe') or data.startswith(b'\xfe\xff'):
        # UTF-16 (laisse Python gérer l'endianness)
        text = data.decode('utf-16', errors='ignore')
    elif data.startswith(b'\xef\xbb\xbf'):
        text = data.decode('utf-8-sig', errors='ignore')
    else:
        # Repli sur utf-8 puis latin-1
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('latin-1', errors='ignore')
    for line in text.splitlines():
        yield line

def _normalize_endpoint(path: str) -> str:
        """Normalise l'endpoint en remplaçant les segments d'ID numériques par :id.
        Exemples :
            /profile/8 -> /profile/:id
            /like/15 -> /like/:id
            /follow/5 -> /follow/:id
        Laisse les segments non-numériques inchangés.
        """
        if not path:
                return path
        return re.sub(r"/(?:\d+)(?=$|/)", "/:id", path)

def analyze_logs(log_file_path: str, include_system: bool = False, build_markov: bool = False, infer_login: bool = False):
    """Analyse le fichier de log et retourne les statistiques.

    include_system : inclure ou non les lignes sans nom d'utilisateur explicite (messages de démarrage) sous l'utilisateur synthétique 'system'.
    build_markov : construire une chaîne de Markov des transitions entre endpoints normalisés.
    infer_login : tenter d'inférer le succès des tentatives de connexion anonymes basées sur l'apparition ultérieure de nouveaux utilisateurs.
    """
    users: Dict[str, list] = {}
    actions: Dict[str, int] = {}
    endpoint_counts: Dict[str, int] = {}
    sequence: list[Tuple[str, str]] = []  # (verbe, endpoint_normalisé)
    # Pour l'inférence de connexion
    pending_logins: list[int] = []  # indices des tentatives de connexion anonymes
    login_success_map: Dict[int, str] = {}  # index de tentative de connexion -> nom d'utilisateur assigné
    seen_users: set[str] = set()
    line_index = 0

    for raw_line in _iter_decoded_lines(log_file_path):
            parsed = parse_log_line(raw_line)
            if not parsed:
                continue

            username = parsed['username']
            # Ignore les lignes système sauf si demandé
            if username == 'system' and not include_system:
                continue

            # Donne la méthode (premier token) de l'action, par défaut 'UNKNOWN'
            verb = parsed['action'].split()[0] if parsed['action'] else 'UNKNOWN'

            users.setdefault(username, []).append(parsed['action'])
            actions[verb] = actions.get(verb, 0) + 1
            # Extrait le chemin si présent (second token)
            parts = parsed['action'].split()
            if len(parts) >= 2 and parts[1].startswith('/'):
                raw_path = parts[1]
                norm_path = _normalize_endpoint(raw_path)
                endpoint_counts[norm_path] = endpoint_counts.get(norm_path, 0) + 1
                if build_markov:
                    sequence.append((verb, norm_path))
            # On essaye d'inférer les résultats de connexion (appariement séquentiel) (on a pas de log pour dire si c'est un succès)
            if infer_login:
                if username == 'anonymous' and verb == 'POST' and parts[1] == '/login':
                    pending_logins.append(line_index)
                elif username != 'anonymous':
                    # La première apparition d'un nouvel utilisateur déclenche l'assignation de succès si en attente
                    if username not in seen_users and pending_logins:
                        login_idx = pending_logins.pop(0)
                        login_success_map[login_idx] = username
                if username != 'anonymous':
                    seen_users.add(username)
            line_index += 1

    transitions: Dict[Tuple[str, str], int] = {}
    if build_markov and len(sequence) > 1:
        # Construit les transitions par utilisateur pour éviter de mélanger les parcours
        user_sequences: Dict[str, list] = {}
        line_idx = 0
        for raw_line in _iter_decoded_lines(log_file_path):
            parsed = parse_log_line(raw_line)
            if not parsed:
                continue
            username = parsed['username']
            if username == 'system' and not include_system:
                continue
            verb = parsed['action'].split()[0] if parsed['action'] else 'UNKNOWN'
            parts = parsed['action'].split()
            if len(parts) >= 2 and parts[1].startswith('/'):
                norm_path = _normalize_endpoint(parts[1])
                user_sequences.setdefault(username, []).append((verb, norm_path))
            line_idx += 1
        
        # Construit les transitions uniquement à l'intérieur de chaque séquence utilisateur
        for username, user_seq in user_sequences.items():
            if username == 'anonymous':
                continue
            for i in range(len(user_seq) - 1):
                src = user_seq[i][1]
                dst = user_seq[i+1][1]
                transitions[(src, dst)] = transitions.get((src, dst), 0) + 1

    # Calcule les probabilités de transition par endpoint source
    transition_probs: Dict[str, Dict[str, float]] = {}
    if transitions:
        per_src_totals: Dict[str, int] = {}
        for (src, dst), cnt in transitions.items():
            per_src_totals[src] = per_src_totals.get(src, 0) + cnt
        for (src, dst), cnt in transitions.items():
            transition_probs.setdefault(src, {})[dst] = cnt / per_src_totals[src] * 100.0

    login_attempts = len(pending_logins) + len(login_success_map) if infer_login else 0
    login_success = len(login_success_map) if infer_login else 0
    login_failed = len(pending_logins) if infer_login else 0

    return {
        'users': users,
        'actions': actions,
        'total_logs': sum(actions.values()),
        'include_system': include_system,
        'endpoints': endpoint_counts,
        'transitions': transitions,
        'transition_percentages': transition_probs,
        'login_attempts': login_attempts,
        'login_success': login_success,
        'login_failed': login_failed
    }

def print_statistics(stats: Dict[str, Dict], show_markov: bool = False, show_login: bool = False):
    """Affiche les statistiques formatées"""


    # Résumé des endpoints
    if stats.get('endpoints'):
        print("\nEndpoints nombre d'utilisations:")
        for ep, cnt in sorted(stats['endpoints'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {ep}: {cnt}")
        print("\nEndpoints (pourcentage d'utilisation):")
        total_endpoints = sum(stats['endpoints'].values())
        for ep, cnt in sorted(stats['endpoints'].items(), key=lambda x: x[1], reverse=True):
            percent = (cnt / total_endpoints) * 100
            print(f"  {ep}: {percent:.1f}%")    
    
    if show_markov and stats.get('transition_percentages'):
        print("\nPourcentages de transition de la chaîne de Markov :")
        for src, dsts in stats['transition_percentages'].items():
            # Trie les destinations par probabilité décroissante
            top_dsts = sorted(dsts.items(), key=lambda x: x[1], reverse=True)
            dst_str = ", ".join(f"{dst}={prob:.1f}%" for dst, prob in top_dsts)
            print(f"  {src} -> {dst_str}")
    if show_login and stats.get('login_attempts'):
        print("\nRésumé des tentatives de connexion:")
        print(f"  Tentatives de connexion anonymes totales: {stats['login_attempts']}")
        print(f"  Réussies (appariées avec un nouvel utilisateur): {stats['login_success']}")
        print(f"  Échouées / non appariées: {stats['login_failed']}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze application log file for user actions.")
    parser.add_argument("--file", "-f", default="logs.txt", help="Path to log file (default: logs.txt)")
    parser.add_argument("--include-system", action="store_true", help="Include system/server lines without username")
    parser.add_argument("--markov", action="store_true", help="Compute and display Markov chain transitions between endpoints (ID-normalized)")
    parser.add_argument("--login-results", action="store_true", help="Infer success of anonymous POST /login attempts based on subsequent new user appearances")
    args = parser.parse_args()

    if os.path.exists(args.file):
        stats = analyze_logs(
            args.file,
            include_system=args.include_system,
            build_markov=args.markov,
            infer_login=args.login_results
        )
        print_statistics(stats, show_markov=args.markov, show_login=args.login_results)
    else:
        print(f"Log file '{args.file}' not found.")