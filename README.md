# Dust'air
Dispositif autonome pour une mesure de la qualité de l'air, en vélo.

## Introduction
L'usage du vélo, comme moyen de locomotion en ville, entraine souvent des irritations des voies respiratoires, surtout l'hiver.
Est-il possible de quantifier la pollution atmospherique sur un trajet/horaire, puis de limiter l'exposition pour diminuer ces irritations ?

## Idée
Un boitier autonome à fixer sur le porte bagage du vélo qui mesurrait en continue le niveau de pollution. L'idéal serait d'enregistrer la position avec un GPS pour avoir la position et l'heure de chaque échantillon. Les irriation étant plutot l'hiver, il est aussi interessant d'ajouter un capteur de temperature.

## Bibliographie

## Version 0
Le premier prototype utilisera beaucoup de composants recyclés pour limiter le coût. En concéquence, ce prototype ne sera ni optimal en consomation electrique, en autonomie, en taille, ... En particulier, seront re-utilisé:

* Raspberry pi B2: c'est un ordinateur mono-carte. On pourra le remplacer par le rapberry-pi zero voir même par un microcontroleur ESP32 ou autre Arduino pour limiter la consomation. Bien que consommant beaucoup, le RPi2 offre 4 port USB, 1 UART (ou 2 ? https://www.rs-online.com/designspark/raspberry-pi-2nd-uart-a-k-a-bit-banging-a-k-a-software-serial)
* Power bank 22Ah: Immense et sur-dimentionnée elle fournit le 5V et l'interupteur marche-arret. L'autonomie devrait être de plusieurs jours.



