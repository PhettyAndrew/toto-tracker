from django.shortcuts import render
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium
import serial.tools.list_ports


# Create your views here.


def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None

    geolocator = Nominatim(user_agent='measurements')

    ip_ = get_ip_address(request)
    print(ip_)
    ip = '105.160.31.207'
    country, city, lat, lon = get_geo(ip)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # initial folium map
    m = folium.Map(width="100%", height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)
    # location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                  icon=folium.Icon(color='purple')).add_to(m)

    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    portList = []

    for onePort in ports:
        portList.append(str(onePort))
        print(str(onePort))

    #val = input("select Port: COM")
    val = 5

    for x in range(0, len(portList)):
        if portList[x].startswith("COM" + str(val)):
            portVar = "COM" + str(val)
            print(portList[x])

    serialInst.baudrate = 300
    serialInst.port = portVar
    serialInst.open()

    while serialInst:
        if serialInst.in_waiting:
            packet = serialInst.readline()
            ip_a = packet[1:15]
            ip_b = ip_a.decode('utf')
            country_b, city_b, lat_b, lon_b = get_geo(ip_b)

            # location coordinates
            d_lat = lat_b
            d_lon = lon_b
            pointB = (d_lat, d_lon)

            location = geolocator.reverse([d_lat, d_lon])
            destination = location.address

            current_location = geolocator.reverse([l_lat, l_lon])
            current_address = current_location.address

            # distance calculation
            distance = round(geodesic(pointA, pointB).km, 2)

            # folium map modification
            m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon),
                           zoom_start=get_zoom(distance))
            # location marker
            folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                          icon=folium.Icon(color='purple')).add_to(m)
            # destination marker
            folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=city_b['city'],
                          icon=folium.Icon(color='red', icon='cloud')).add_to(m)

            # draw the line between location and destination
            line = folium.PolyLine(locations=[pointA, pointB], weight=2, color='blue')
            m.add_child(line)


            m = m._repr_html_()

            context = {
                'distance': distance,
                'destination': destination,
                'current_address': current_address,
                'map': m,
            }

            return render(request, 'measurements/main.html', context)
