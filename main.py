import random
import streamlit as st
import pydeck as pdk
import json
import requests
# import services

API = 'https://elyssa.tsaas.tn/api'

INIT_REQ = {
    "type": "init",
    "pays": "tunisie"
}

COLORS = [
    # "#ffffff",
    "#ffe3aa",
    "#ffc655",
    "#ffaa00",
    "#ff7100",
    "#ff3900",
    "#ff0000",
    "#d50621",
    "#aa0b43",
    "#801164",
    "#551785",
    "#2b1ca7",
    "#0022c8",
]

COLORS_CONVERTED = [
    # [255, 255, 255, 255],
    [255, 227, 170, 255],
    [255, 198, 85, 255],
    [255, 170, 0, 255],
    [255, 113, 0, 255],
    [255, 57, 0, 255],
    [255, 0, 0, 255],
    [213, 6, 33, 255],
    [170, 11, 67, 255],
    [128, 17, 100, 255],
    [85, 23, 133, 255],
    [43, 28, 167, 255],
    [0, 34, 200, 255],
]

with open('maps/gouvernorat.json', 'r') as f:
    geojson_data = json.load(f)

st.set_page_config(page_title='Projet ELYSSA',  page_icon=":flag-tn:")

if 'maps' not in st.session_state:
    st.session_state['maps'] = {}


def electionRequest(election):
    request = {
        "type": "election"
    }
    return request


@st.cache_data
def get_init():
    response = requests.post(url=API, json=INIT_REQ)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print('init request failed, status code: ', response.status_code)
        return response.text


@st.cache_data
def get_election(election):
    if (election):
        request = {
            "type": "election",
            "pays": "tunisie",
            "code_election": election['code_election']
        }
        response = requests.post(url=API, json=request)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print('init request failed, status code: ', response.status_code)
            return response.text
    else:
        return None


def get_results(election, parti):
    if (election and parti):
        request = {
            "type": "data",
            "pays": "tunisie",
            "code_election": election['code_election'],
            "decoupage": "gouvernorat",
            "variables": [
                {"code_variable": "prc", "code_parti": parti['code_parti']}
            ]
        }
        response = requests.post(url=API, json=request)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print('init request failed, status code: ', response.status_code)
            return response.text
    else:
        return None

# temporary function for state management


def addMapToState(mapObject):
    length = len(st.session_state.maps)
    if length == 0:
        st.session_state.maps = {1: mapObject}
    else:
        # If maps exists and is not empty
        nextKey = max(st.session_state.maps.keys()) + 1
        st.session_state.maps[nextKey] = mapObject
    st.rerun()


@st.cache_data
def returnMap(resultat):
    # if resultat:
    #     st.write(resultat['result']['result'][0]['variables'][0]['resultat'])
    mapChart = st.pydeck_chart(pdk.Deck(
        map_provider=None,
        initial_view_state=pdk.ViewState(
            latitude=33.9989,
            longitude=10.1658,
            zoom=5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'GeoJsonLayer',
                data=geojson_data,
                get_fill_color=COLORS_CONVERTED[0],
                pickable=True,
                auto_highlight=True,
            ),
        ]
    ), use_container_width=False,)
    return mapChart


result = get_init()
election_list = [election['nom']for election in result['elections']]


def main():
    st.title('Projet ELYSSA')
    # st.write(st.session_state.maps)
    container = st.container(border=True, height=600)
    with container:
        for key, value in st.session_state.maps.items():
            returnMap(value)


def sideBar():
    selected_parti = None
    selected_election = st.selectbox(
        label="Choisissez une élection",
        placeholder='Liste des élections',
        index=None,
        options=result['elections'],
        format_func=lambda x: x['nom']
    )
    if selected_election:
        selected_parti = st.selectbox(
            label="Choisissez un parti",
            placeholder="Liste des partis",
            index=None,
            options=get_election(selected_election)['partis'],
            format_func=lambda x: x['denomination_fr']
        )

    else:
        st.selectbox(
            label="Choisissez un parti",
            index=None,
            options=['A', 'B'],
            disabled=True,
            placeholder="Liste des partis"
        )
    if st.button("Ajoutez", disabled=not selected_parti):
        results = get_results(selected_election, selected_parti)
        mapObject = {"election": selected_election,
                     "parti": selected_parti, "result": results}
        selected_election = None
        selected_parti = None
        addMapToState(mapObject)


if __name__ == "__main__":
    main()
    with st.sidebar:
        sideBar()
