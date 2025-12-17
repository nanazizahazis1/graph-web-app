import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Graph Web App", layout="wide")
plt.style.use("seaborn-v0_8-whitegrid")

if "page" not in st.session_state:
    st.session_state.page = "members"
if "lang" not in st.session_state:
    st.session_state.lang = "Indonesia"

# DICTIONARY BAHASA (Full Update)
texts = {
    "English": {
        "nav": "Navigation",
        "lang": "Select Language",
        "btn_members": "Group Members",
        "btn_graph": "Graph Visualization",
        "btn_map": "City Routing",
        "title_members": "Team Member Profiles",
        "title_graph": "Graph Theory Visualization",
        "title_map": "City Routing & Dijkstra",
        "label_nodes": "Number of Nodes",
        "label_edges": "Number of Edges",
        "btn_generate": "Generate Graph",
        "degree": "Degree Table",
        "adj": "Adjacency Matrix",
        "select_prov": "Select Province",
        "from": "Origin City",
        "to": "Destination City",
        "show_route": "Show Shortest Route",
        "dist": "Total Distance",
        "path": "Route Path",
        "err_path": "Path not connected",
        "map_desc": "Gray lines show original route connections. Red shows the shortest path."
    },
    "Indonesia": {
        "nav": "Navigasi Aplikasi",
        "lang": "Pilih Bahasa",
        "btn_members": "Anggota Grup",
        "btn_graph": "Visualisasi Graf",
        "btn_map": "Rute Kota",
        "title_members": "Profil Anggota Tim",
        "title_graph": "Visualisasi Teori Graf",
        "title_map": "Rute Kota & Dijkstra",
        "label_nodes": "Jumlah Node",
        "label_edges": "Jumlah Edge",
        "btn_generate": "Buat Graf",
        "degree": "Tabel Derajat",
        "adj": "Matriks Adjasensi",
        "select_prov": "Pilih Provinsi",
        "from": "Kota Asal",
        "to": "Kota Tujuan",
        "show_route": "Tampilkan Rute Terpendek",
        "dist": "Total Jarak",
        "path": "Jalur Rute",
        "err_path": "Jalur tidak terhubung",
        "map_desc": "Garis abu-abu menunjukkan koneksi rute asli. Merah menunjukkan jalur terpendek."
    }
}

T = texts[st.session_state.lang]

# ======================
# SIDEBAR
# ======================
st.sidebar.title(T["nav"])
st.sidebar.write("---")

sel_lang = st.sidebar.selectbox(T["lang"], ["Indonesia", "English"], 
                                index=0 if st.session_state.lang == "Indonesia" else 1)
if sel_lang != st.session_state.lang:
    st.session_state.lang = sel_lang
    st.rerun()

if st.sidebar.button(T["btn_members"]):
    st.session_state.page = "members"
    st.rerun()
if st.sidebar.button(T["btn_graph"]):
    st.session_state.page = "graph"
    st.rerun()
if st.sidebar.button(T["btn_map"]):
    st.session_state.page = "map"
    st.rerun()

# ======================
# DATA KABUPATEN/KOTA LENGKAP
# ======================
java_data = {
    "Jawa Barat": {
        "Bandung": (-6.9175, 107.6191), "Bandung Barat": (-6.8451, 107.5204), "Bekasi": (-6.2307, 106.9936), "Bogor": (-6.5971, 106.8060), "Ciamis": (-7.3274, 108.3551), "Cianjur": (-6.8222, 107.1394), "Cirebon": (-6.7320, 108.5530), "Garut": (-7.2279, 107.9087), "Indramayu": (-6.3273, 108.3249), "Karawang": (-6.3042, 107.2935), "Kuningan": (-6.9764, 108.4845), "Majalengka": (-6.8361, 108.2274), "Pangandaran": (-7.7011, 108.4945), "Purwakarta": (-6.5514, 107.4433), "Subang": (-6.5715, 107.7587), "Sukabumi": (-6.9277, 106.9300), "Sumedang": (-6.8402, 107.9213), "Tasikmalaya": (-7.3274, 108.2207), "Banjar": (-7.3716, 108.5350), "Cimahi": (-6.8722, 107.5432), "Depok": (-6.4025, 106.7942)
    },
    "Jawa Tengah": {
        "Banjarnegara": (-7.3967, 109.6974), "Banyumas": (-7.5133, 109.2941), "Batang": (-6.9150, 109.7289), "Blora": (-6.9697, 111.4190), "Boyolali": (-7.5342, 110.5944), "Brebes": (-6.8704, 109.0416), "Cilacap": (-7.7277, 109.0263), "Demak": (-6.8948, 110.6387), "Grobogan": (-7.0872, 110.9170), "Jepara": (-6.5888, 110.6777), "Karanganyar": (-7.5962, 110.9515), "Kebumen": (-7.6699, 109.6521), "Kendal": (-6.9202, 110.2036), "Klaten": (-7.7032, 110.6025), "Kudus": (-6.8048, 110.8407), "Magelang": (-7.4706, 110.2178), "Pati": (-6.7533, 111.0371), "Pekalongan": (-6.8886, 109.6753), "Pemalang": (-6.8906, 109.3813), "Purbalingga": (-7.3875, 109.3676), "Purworejo": (-7.7145, 110.0074), "Rembang": (-6.7063, 111.3384), "Semarang": (-6.9667, 110.4167), "Sragen": (-7.4267, 111.0222), "Sukoharjo": (-7.6833, 110.8333), "Tegal": (-6.8676, 109.1370), "Temanggung": (-7.3175, 110.1764), "Wonogiri": (-7.8485, 110.9261), "Wonosobo": (-7.3602, 109.9042), "Salatiga": (-7.3262, 110.5012), "Surakarta": (-7.5708, 110.8214)
    },
    "Jawa Timur": {
        "Bangkalan": (-7.0455, 112.7441), "Banyuwangi": (-8.2192, 114.3691), "Blitar": (-8.0983, 112.1681), "Bojonegoro": (-7.1502, 111.8817), "Bondowoso": (-7.9135, 113.8215), "Gresik": (-7.1592, 112.6519), "Jember": (-8.1724, 113.7003), "Jombang": (-7.5461, 112.2331), "Kediri": (-7.8167, 112.0167), "Lamongan": (-7.1204, 112.4157), "Lumajang": (-8.1331, 113.2226), "Madiun": (-7.6298, 111.5239), "Magetan": (-7.6542, 111.3283), "Malang": (-7.9666, 112.6326), "Mojokerto": (-7.4705, 112.4401), "Nganjuk": (-7.6043, 111.9045), "Ngawi": (-7.4029, 111.4449), "Pacitan": (-8.2071, 111.0921), "Pamekasan": (-7.1601, 113.4824), "Pasuruan": (-7.6445, 112.9037), "Ponorogo": (-7.8665, 111.4665), "Probolinggo": (-7.7569, 113.2161), "Sampang": (-7.1197, 113.2458), "Sidoarjo": (-7.4478, 112.7183), "Situbondo": (-7.7019, 113.9940), "Sumenep": (-7.0084, 113.8621), "Trenggalek": (-8.1000, 111.7167), "Tuban": (-6.8944, 112.0571), "Tulungagung": (-8.0667, 111.9000), "Batu": (-7.8705, 112.5271), "Surabaya": (-7.2575, 112.7521)
    }
}

# ======================
# PAGE 1 — MEMBERS
# ======================
if st.session_state.page == "members":
    st.title(T["title_members"])
    st.write("---")
    members = [
        {"name": "Tsabila Azka Amalina", "id": "021202500008", "role": "Project Leader", "desc": "Koordinasi tim & struktur Streamlit.", "photo": "assets/azka.jpeg"},
        {"name": "Shilvia Novicha Silitonga", "id": "021202500030", "role": "Data Visualization", "desc": "Visualisasi graf & peta.", "photo": "assets/silvia.jpeg"},
        {"name": "Nana Azizah Azis", "id": "021202500015", "role": "Graph Theory Analyst", "desc": "Implementasi algoritma Dijkstra.", "photo": "assets/nana.jpeg"}
    ]
    cols = st.columns(3)
    for col, m in zip(cols, members):
        with col:
            st.image(m["photo"], width=220)
            st.subheader(m["name"])
            st.write(f"ID: {m['id']}")
            st.write(f"Role: {m['role']}")
            st.caption(m["desc"])

# ======================
# PAGE 2 — GRAPH
# ======================
elif st.session_state.page == "graph":
    st.title(T["title_graph"])
    st.write("---")
    c1, c2 = st.columns(2)
    with c1: num_nodes = st.number_input(T["label_nodes"], 1, 30, 8)
    with c2: num_edges = st.number_input(T["label_edges"], 0, 100, 12)

    if st.button(T["btn_generate"]):
        G = nx.gnm_random_graph(num_nodes, num_edges)
        fig, ax = plt.subplots(figsize=(8, 5))
        nx.draw(G, with_labels=True, node_color='skyblue', ax=ax)
        st.pyplot(fig)
        st.subheader(T["degree"])
        st.dataframe(pd.DataFrame(G.degree(), columns=["Node", "Degree"]), use_container_width=True)
        st.subheader(T["adj"])
        st.dataframe(nx.to_pandas_adjacency(G, dtype=int), use_container_width=True)

# ======================
# PAGE 3 — MAP
# ======================
elif st.session_state.page == "map":
    st.title(T["title_map"])
    st.write(T["map_desc"])
    st.write("---")

    prov = st.selectbox(T["select_prov"], list(java_data.keys()))
    city_names = sorted(list(java_data[prov].keys()))

    col1, col2 = st.columns(2)
    with col1: start_city = st.selectbox(T["from"], city_names)
    with col2: end_city = st.selectbox(T["to"], city_names, index=len(city_names)-1)

    show_route = st.checkbox(T["show_route"])

    # Global connection
    all_coords = {}
    for p_cities in java_data.values(): all_coords.update(p_cities)
    
    G_map = nx.Graph()
    for c, coord in all_coords.items(): G_map.add_node(c, pos=coord)
    
    # Hubungkan kota radius < 130km
    names = list(all_coords.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = geodesic(all_coords[names[i]], all_coords[names[j]]).km
            if d < 130: G_map.add_edge(names[i], names[j], weight=d)

    m = folium.Map(location=all_coords[start_city], zoom_start=8)
    
    # Jalur abu-abu
    for u, v in G_map.edges():
        folium.PolyLine([all_coords[u], all_coords[v]], color="gray", weight=1, opacity=0.3).add_to(m)

    # Titik kota
    for c, coord in java_data[prov].items():
        folium.CircleMarker(location=coord, radius=5, color="blue", fill=True, tooltip=c).add_to(m)

    if show_route:
        try:
            path = nx.shortest_path(G_map, source=start_city, target=end_city, weight='weight')
            dist = nx.shortest_path_length(G_map, source=start_city, target=end_city, weight='weight')
            st.success(f"{T['dist']}: {dist:.2f} km")
            st.info(f"{T['path']}: {' -> '.join(path)}")
            folium.PolyLine([all_coords[s] for s in path], color="red", weight=4).add_to(m)
        except:
            st.error(T["err_path"])

    st_folium(m, width="100%", height=500)