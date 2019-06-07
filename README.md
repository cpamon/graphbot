# GraphBot - Pràctica Python

Pràctica del GraphBot en Python, per l'assignatura de LP.

### Prerequisits

Per tal d'executar _graphBot_ correctament, es necessiten descarregar unes llibreries addicionals, en cas que no les tingueu ja descarregades. També es necessita el fitxer _graphBot_func_ que conté funcions necessàries. 

```
pip3 install python-telegram-bot
pip3 install networkx
pip3 install haversine
pip3 install FuzzyWuzzy
pip3 install staticmap
pip3 install requests
pip3 install pandas
```

## Descobrint el programa

GraphBot és un bot de Telegram capaç de construir grafs que representen ciutats del món. Un cop creat un graf, podem representarlo en el mapa, o cercar una ruta entre dues ciutats.

### Per començar

Per començar li podem enviar la comanda /start al bot.

```
Usuari: /start
Bot: Hola! Envia'm la teva ubicació
     Si necessites ajuda, prem /help
```

Per crear un graf on els nodes són les ciutats de més de 250000 habitants, i les arestes són aquelles ciutats que estàn a menys de 500 kilòmetres.

```
Usuari: /graph 500 250000
```

### Plots i route

Un cop tenim el graf creat, podem "jugar" amb ell, projectant-lo sobre un mapa de la terra o bé buscar una ruta entre dues ciutats. Per els plots, haurem d'especificar unes coordenades si no li hem passat una ubicació prèviament

```
Usuari: /plotgraph 1000
```
![Mapa 1](https://i.imgur.com/4eDFWyW.jpg)

```
Usuari: /route "Sevilla, es" "Paris, fr"
```
![Mapa 2](https://i.imgur.com/RJMzoot.jpg)

### Llista completa de comandes
- /graph _⟨distance⟩ ⟨population⟩_  -  Crea un graf on:
nodes = ciutats del mon amb població major o igual a   ⟨population⟩
edges = distancia entre ciutats menor o igual a ⟨distance⟩

- /nodes - Escriu el nombre de nodes en el graf

- /edges - Escriu el nombre d'arestes en el graf

- /components - Escriu el nombre de components connexs en el graf

- /plotpop ⟨dist⟩ [⟨lat⟩ ⟨lon⟩] - Mostra un mapa amb totes les ciutats del graf a distància menor o igual que ⟨dist⟩ de [⟨lat⟩,⟨lon⟩]. Si no s'especifica cap ubicació, es pren la de l'usuari.  Cada ciutat es mostra amb un cercle, de radi proporcional a la seva població

- /plotgraph ⟨dist⟩ [⟨lat⟩ ⟨lon⟩] - Mostra un mapa amb totes les ciutats del graf a distància menor o igual que ⟨dist⟩ de ⟨lat⟩,⟨lon⟩ i les arestes que es connecten. Si no s'especifica cap ubicació, es pren la de l'usuari

- /route ⟨src⟩ ⟨dst⟩ - Mostra un mapa amb les arestes del camí més curt per anar entre dues ciutats ⟨src⟩ i ⟨dst⟩. La sintàxi de les ciutats és "_Nom_, _codiPaís_"




## Autor

* **Carles Pàmies Montero** - carles.pamies@est.fib.upc.edu

