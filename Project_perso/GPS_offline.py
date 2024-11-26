import osmnx as ox
import networkx as nx
import folium
from geopy.geocoders import Nominatim  # API qui contient des fonctionnalités et des données géographiques

# Définir les coordonnées de départ et d'arrivée
def geocode_address(address):
    geolocalisation = Nominatim(user_agent="toti")
    location = geolocalisation.geocode(address)

    if location:
        return (float(location.latitude), float(location.longitude))  # Les coordonnées seront transformées en latitude et longitude
    else:
        raise ValueError(f"Adresse non trouvée : {address}")

adresse_depart = "6 place Auguste Rodin, Villejuif"
adresse_arrivee = "Belle Épine, Rungis"

start_point = geocode_address(adresse_depart)
end_point = geocode_address(adresse_arrivee)

# Télécharger le réseau routier pour la zone d'intérêt => G représente un graphe (en quelque sorte une base de données car il contient des informations sur des milliers de nœuds et d'arêtes) ==> la distance est exprimée en mètres ==> cette distance permet de définir la zone de téléchargement du réseau routier, sans quoi on n'aurait pas les nœuds et les coordonnées liées à certaines zones au-delà de cette distance.
G = ox.graph_from_point(start_point, dist=7000, network_type='drive', simplify=False)  # start_point doit être une liste (latitude, longitude), G va nous donner une zone avec toutes les routes possibles pour rejoindre la destination

# Ajouter les vitesses et les temps de parcours moyens des automobilistes (données réelles collectées par osmnx) pour chaque arête dans G afin de calculer ensuite les temps de l'itinéraire
# Cela est très important car sans ces informations, l'algorithme ne pourrait pas évaluer correctement le temps de parcours.

G = ox.add_edge_speeds(G)  # Cette fonction attribue une vitesse estimée (speed_kph) à chaque arête du graphe en fonction du type de route. Les vitesses sont estimées à partir de données typiques pour différents types de routes (par exemple, autoroutes, rues résidentielles).

# Ajouter aussi les temps de trajet calculés aux arêtes grâce aux vitesses ajoutées ci-dessus
G = ox.add_edge_travel_times(G)

# Trouver les nœuds les plus proches des points de départ et d'arrivée ==> Un nœud est un point sur la carte. Généralement, un nœud est relié par une ou plusieurs arêtes (l'itinéraire) avec un autre nœud. Le réseau routier est une sorte de graphe avec beaucoup de nœuds et d'arêtes qui désignent les routes à suivre.
# Latitude et longitude peuvent être considérées comme les axes X et Y dans ce graphe.

# AXE DES X      #AXE DES Y 
orig_node = ox.distance.nearest_nodes(G, start_point[1], start_point[0])  # Le premier élément de la liste start_point correspond à la longitude, donc on le met dans l'argument X (longitude), puis l'argument Y (latitude).
dest_node = ox.distance.nearest_nodes(G, end_point[1], end_point[0])

# Calculer l'itinéraire le plus court
try:
    route = nx.shortest_path(G, orig_node, dest_node, weight="travel_time", method="dijkstra")  # On utilise l'algorithme de Dijkstra pour trouver le chemin le plus court avec le poids des arêtes calculé selon le temps de trajet.
except nx.NetworkXNoPath:
    print("Pas de chemin disponible : veuillez réajuster à la hausse le paramètre 'dist' à la ligne 34.")

# Obtenir les positions des nœuds pour l'affichage
pos = nx.get_node_attributes(G, 'x'), nx.get_node_attributes(G, 'y')
pos = {k: (pos[0][k], pos[1][k]) for k in pos[0].keys()}

# Créer une carte interactive centrée sur le point de départ
m = folium.Map(location=start_point, zoom_start=14)

# Ajouter l'itinéraire à la carte
route_coords = [(pos[node][1], pos[node][0]) for node in route]
folium.PolyLine(route_coords, color='red', weight=10, opacity=0.4).add_to(m)

# Ajouter des marqueurs pour le point de départ et d'arrivée
folium.Marker(location=start_point, popup='Départ', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=end_point, popup='Arrivée', icon=folium.Icon(color='red')).add_to(m)

# Calculer la distance = somme de toutes les arêtes du graphe
route_gdf = ox.routing.route_to_gdf(G, route)
route_length = route_gdf["length"].sum() / 1000  # Convertir en kilomètres
print(f"Distance totale de l'itinéraire : {route_length:.2f} kilomètres")

# Ajouter le temps de trajet total de l'itinéraire
total_travel_time = sum(ox.utils_graph.get_route_edge_attributes(G, route, 'travel_time'))
total_travel_time_minutes = total_travel_time / 60  # Convertir en minutes
print(f"Temps total de l'itinéraire : {total_travel_time_minutes:.2f} minutes")

# Sauvegarder la carte dans un fichier HTML
m.save("interactive_map.html")

print("La carte interactive avec l'itinéraire a été sauvegardée dans 'interactive_map.html'.")
