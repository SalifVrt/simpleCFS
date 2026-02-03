*N.B. : Il ne s’agit pas de reproduire le code source du noyau Linux, mais d’en comprendre et d’en simuler le fonctionnement conceptuel.*
 
# Modèle et Hypothèses

On considère le modèle simplifié suivant :

    Un seul processeur (mono-cœur), pas de migration de tâches, pas de support SMP.
    Pas d'arbre rouge-noir (red-black tree) ; la sélection de la tâche suivante se fait par un parcours linéaire de la file d'attente (runqueue).
    Pas de gestion de la latence interactive, pas de wakeup preemption, etc.
    Le temps est exprimé en millisecondes (ms), sous forme de nombres réels, avec une précision au centième.
    
    **Paramètres par défaut :**
        Granularité minimale : Δ = 0,75 ms
        Période d’ordonnancement : L = 6 ms

    **Mise à jour du vruntime :** afin de simplifier l’implémentation, le vruntime des tâches est mis à jour uniquement au moment de l’invocation de l’ordonnanceur.

    **Équité à l'insertion :** pour les nouvelles tâches ou celles de retour d'E/S, le vruntime initial est égal au minimum des vruntime des tâches présentes dans la runqueue à cet instant.

    **Déclenchement :** l’ordonnanceur est invoqué :
        à la fin du *time slice* de la tâche en cours ;
        lorsque la tâche courante se termine ;
        lorsque la tâche passe en mode E/S (I/O).

    **Non-préemption :** au retour d’une E/S, la tâche est insérée dans la runqueue sans préemption immédiate de la tâche en cours, même si son retard est important.

# Travail demandé

    Implémenter le simulateur dans le langage de votre choix.
    Calculer et afficher au moins deux métriques d’évaluation (cf cours, ex: temps de rotation moyen, temps d'attente, taux d'utilisation CPU).
    Afficher l’évolution de l’ordonnancement sous forme de log textuel ou via un diagramme de Gantt.

# Entrée du modèle

Le programme lit un fichier texte où chaque ligne correspond à un processus :
Identifiant | Temps_Arrivée | Alternance CPU / E/S ...

**Exemple de données :**

A 0 0.5 5 20
B 0 10 8 0.96 5 0.75
 

**Le processus A :**

    arrive à t = 0 ms.
    exécute 0,5 ms de calcul CPU.
    effectue 5 ms d'E/S.
    termine par 20 ms de calcul CPU.

