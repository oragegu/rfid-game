# rfid-game

L'utilisateur peut choisir entre différentes options telles que "calibrate", "hide and seek" et "soleil". 

Chaque option appelle une fonction qui effectue une action spécifique.

La fonction "calibrate" permet de calibrer le système en demandant à chaque joueur de passer son tag devant l'antenne, et en enregistrant les noms et les tags dans un fichier texte.

La fonction "hide and seek" est un jeu de cache-cache. Le système attend le début du jeu, puis démarre un chronomètre de 3 secondes avant de commencer à lire les tags. Si un tag est détecté à une distance inférieure à 1 unité (à compléter), il est considéré comme "trouvé".

La fonction "one_two_three_sun" est également un jeu, où le système compte de 1 à 3, joue un son et capture tous les tags présents devant l'antenne.
