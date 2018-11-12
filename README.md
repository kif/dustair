# Dust'air
Dispositif autonome pour une mesure de la qualité de l'air, en vélo.

## Introduction
L'usage du vélo, comme moyen de locomotion en ville, entraine souvent des irritations des voies respiratoires, surtout l'hiver.
Est-il possible de quantifier la pollution atmospherique sur un trajet/horaire, puis de limiter l'exposition pour diminuer ces irritations ?

## Idée
Un boitier autonome à fixer sur le porte bagage du vélo qui mesurrait en continue le niveau de pollution. L'idéal serait d'enregistrer la position avec un GPS pour avoir la position et l'heure de chaque échantillon. Les irriation étant plutot l'hiver, il est aussi interessant d'ajouter un capteur de temperature.

## Bibliographie

## Prototype, version 0
Le premier prototype utilisera beaucoup de composants recyclés pour limiter le coût. En concéquence, ce prototype ne sera ni optimal en consomation electrique, en autonomie, en taille, ... En particulier, seront re-utilisé:

* Raspberry pi B2: c'est un ordinateur mono-carte. On pourra le remplacer par le rapberry-pi zero voir même par un microcontroleur ESP32 ou autre Arduino pour limiter la consomation. Bien que consommant beaucoup, le RPi2 offre 4 port USB, 1 UART (ou 2 ? https://www.rs-online.com/designspark/raspberry-pi-2nd-uart-a-k-a-bit-banging-a-k-a-software-serial)
* Power bank 22Ah: Immense et sur-dimentionnée elle fournit le 5V et l'interupteur marche-arret. L'autonomie devrait être de 
plusieurs jours.

Les composants additionnels sont: Un recepteur GPS (cout: 8€) et un capteur de particule SDS021 (cout 18€). Vous trouverez dans le repertoire "spec" les fiches techniques de ces composants. 

La partie CAO est disponible sur Thingiverse:
https://www.thingiverse.com/thing:2787132

## Prototype, version 1
On utilise comme base un ESP32, alimenté par une batterie Li-Ion directement sur la carte comme celui-ci (<10€):
https://www.ebay.fr/itm/WEMOS-ESP32-WiFi-and-Bluetooth-Battery-Development-Tool-AP-STA-AP-STA-for-Lua-/173252493037

Il est programmé en micropython, l'autonomie en stocage est de 8h à raison d'un point par seconde et de 3h par batterie (rechageable en USB).

