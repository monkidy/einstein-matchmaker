# EINSTEIN Matchmaker, film de soumission V1 privé : preuves, storyboard, contrôle qualité

**Mis à jour le 31/10 à 18h30.** Ce dossier accompagne le film de soumission. À sa création il n'était ni publié ni soumis ; depuis, Hichem a donné son accord explicite, le film est publié dans le dépôt public et la candidature est enregistrée chez l'organisateur avec son lien. Le nom de fichier garde le suffixe `_prive` de sa première version : c'est le même contenu, même empreinte.

- **Commande :** Hichem, 31/10/2026, « on va faire la démo », avec l'idée que ce soit Asso
  qui présente. Texte parlé validé par lui avant tout calcul de voix, selon la règle du
  30/10. Réalisation : Claude.
- **Concours :** 3alet Hackathon 2026, JigJoy et NTP Novi Sad, piste EINSTEIN, CU-0070.
  Clôture le 31/10 à 20:00 CET. La candidature est **déjà soumise** (dépôt et textes) ; ce
  film sert à remplir le champ vidéo lors d'une resoumission.
- **Fichier :** `EINSTEIN_MATCHMAKER_DEMO_V1_prive.mp4`, 1:32,88 (92,877 s), 1920x1080 à
  25 i/s, H.264, son AAC 48 kHz mono, sous-titres anglais incrustés.
- **sha256 :** `9a464ed68f5d2c94d12c7674e418ad432bec0b008df22a62f93a3db4455f314d`
  (9 467 827 octets).

## 1. En une phrase

Asso présente un système où quatre agents travaillent en même temps sur le défi technique
d'une entreprise, et qui refuse de proposer quand les preuves manquent. Chaque chiffre à
l'écran est lu dans les fichiers d'un run réellement vérifié.

## 2. Le storyboard, et la preuve de chaque phrase

| Plan | Texte parlé | Ce qui est à l'écran | Preuve |
|---|---|---|---|
| S1 | A company has a problem... Finding a name is easy. Being right is not. | le défi réel de Pulmoteh d.o.o., cité mot à mot | `results.json`, claim sur `data/companies.json` |
| S2 | I am Asso, from SYSTASYS... No hosted API. No key. | les 4 identifiants d'agents, 0 appel hébergé, 0 appel payant | `receipt.json` |
| S3 | Two of them think at the very same instant... Sixty three percent of the compute. | 5009 / 7933 / 63,1 %, et la bande de concurrence | `evidence/concurrency-block1-verified.json` |
| S4 | Then an independent critic reads the proposal... the system says no. | la proposition acceptée, son empreinte d'enregistrement, son URL source | `results.json`, 16 claims vérifiés |
| S5 | Two proposals were accepted. One was refused on the evidence. Three ran out of time. | les trois sortes d'issues, comptées à part | `results.json` du bras parallèle |
| S6 | We do not claim that four agents answer better than one. | `hidden_jury_gold_available: false`, `usefulness_uplift_proven: false` | `independent-verification.json` |
| S7 | A system that cannot refuse cannot be trusted when it accepts. | carton final, adresse du dépôt |, |

**Pastilles d'honnêteté**, reprises de la discipline du film ANIMA et présentes sur chaque
plan : `REAL RUN . 31 Oct 2026 . Qwen3-4B Q4_K_M, CPU only . organizer corpus v2 .
fictional dataset . edited for length` pour les plans de démonstration,
`DRAWN FROM THE TRACE . no interpolated value` pour les figures, et sur le carton final
`Narration: synthetic voice (Asso, SYSTASYS). Entry by Hichem Benali, solo.`

Cette dernière ligne est délibérée : un dossier dont tout l'argument est qu'il ne triche
pas sur sa concurrence ne peut pas laisser croire qu'une personne parle.

## 3. La voix

Recette strictement celle validée le 22/10 et réutilisée pour ANIMA, aucune variation :

- modèle `Qwen/Qwen3-TTS-12Hz-0.6B-Base`, révision `5d83992436eae1d760afd27aff78a71d676296fc`
- référence vocale sha256 `047aaa0546eece2109401775112bafdeb52fc9a0b254accf5c7829f60b093069`
- graine 1234, `x_vector_only_mode` vrai, langue English
- calcul sur l'organe de voix, en priorité minimale (`nice 19`, 2 fils) pour ne pas prendre
  de processeur à la production de la firme, qui était déjà chargée
- `Sistah-ziss` est écrit dans le texte envoyé au moteur, graphie validée le 28/10 pour que
  SYSTASYS soit prononcé correctement. Les sous-titres écrivent **SYSTASYS**.

Contrôle automatique de chaque segment, transcription et note de naturel :

| Segment | durée | mots mal entendus | naturel | voix vs référence |
|---|---|---|---|---|
| S1 | 8,59 s | 0,0 % | 4,38 | 0,992 |
| S2 | 13,63 s | 2,6 % | 4,41 | 0,992 |
| S3 | 15,63 s | 0,0 % | 4,42 | 0,991 |
| S4 | 15,07 s | 4,4 % | 4,39 | 0,991 |
| S5 | 12,99 s | 0,0 % | 4,42 | 0,992 |
| S6 | 11,07 s | 0,0 % | 4,40 | 0,992 |
| S7 | 10,19 s | 0,0 % | 4,40 | 0,991 |

Tous sous le seuil de 5 %. **Aucune reprise n'a été nécessaire.** Durée parlée 87,17 s,
calcul 1193,7 s.

## 4. Les sous-titres

Ils viennent du **texte écrit**, pas de la transcription. C'est un correctif : la première
version affichait `Sista Ziss` parce qu'elle recopiait ce que la transcription avait
entendu. Les horodatages, eux, viennent du relevé mot à mot et sont reportés sur le texte
écrit par position, ce qui est sûr tant que le taux d'erreur reste bas.

Mise en page figée dans un fichier ASS qui porte sa propre résolution de référence
(1920x1080). Sans cela, le filtre met en page dans un cadre de 384 pixels et le texte
atterrit au milieu de l'écran, deux fois trop gros : c'est le défaut de la V0.

## 5. Défauts connus qui restent, à juger

Dits ici plutôt que découverts par le réviseur :

1. **3 cues sur 30 dépassent 42 caractères sur une ligne.** Lisible, mais au-dessus de la
   norme de confort.
2. **3 cues durent moins de 1,2 s**, la plus brève 0,76 s. Elles suivent des phrases très
   courtes de la narration ; les allonger les ferait mordre sur la suivante.
3. **4 cues dépassent 19 caractères par seconde.** La vitesse est celle de la parole ; la
   réduire imposerait de condenser le texte affiché, donc de ne plus écrire ce qui est dit.
4. **Le fond des sous-titres suit chaque ligne**, ce qui donne un léger effet d'escalier
   quand la deuxième ligne est plus courte. Cosmétique.
5. **Aucun plan de terminal en mouvement.** Le film est fait de plans fixes avec un très
   léger mouvement de caméra. Un rejeu de session réelle, comme dans ANIMA, serait plus
   vivant ; il n'a pas été fait faute de machine libre, le comparatif occupant la machine
   de calcul.
6. **Zéro chevauchement**, zéro plan débordant dans la bande des sous-titres : un garde-fou
   dans le générateur refuse un plan dont le contenu descend sous 845 pixels.

## 6. Ce qui est demandé à la revue

Vérifier que **chaque affirmation du film est vraie et prouvée**, et que tout ce qui est
mesuré est dit comme mesuré. Le jugement du goût n'est pas demandé, mais tout défaut de
lisibilité est utile.

Points d'attention : la phrase de S3 arrondit 5009 à « five thousand » et 7933 à « nearly
eight thousand » ; les chiffres exacts sont à l'écran. S5 décrit le bras parallèle du bloc
1, pas l'ensemble des blocs. S6 affirme qu'aucun avantage n'est revendiqué, ce que la
mesure confirme : les trois bras acceptent exactement 2 cas sur 6.

## 7. Reproduire

Dans le dépôt public `github.com/monkidy/einstein-matchmaker` :

```bash
python3 scripts/film_plans.py runs/benchmark-v2/block-1/parallel film/plates
python3 scripts/build_film.py film einstein_matchmaker_demo.mp4
```
