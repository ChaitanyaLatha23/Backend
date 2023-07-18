from distutils import dist
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add other allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/asa-change")
async def calculate_asa_change(data: dict):
    entry_id = data.get("entry_id")
    assembly_id = data.get("assembly_id")
    interface_id = data.get("interface_id")

    api_url = f"https://data.rcsb.org/rest/v1/core/interface/{entry_id}/{assembly_id}/{interface_id}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Failed to fetch interface data from RCSB API")

    interface_data = response.json()
    print(interface_data)
    interface_partner = interface_data['rcsb_interface_partner']

    result = {}

    for partner in interface_partner:
        partner_identifier = partner['interface_partner_identifier']
        entity_id = partner_identifier['entity_id']
        asym_id = partner_identifier['asym_id']

        partner_feature = partner['interface_partner_feature']
        unbound_asa_data = None
        bound_asa_data = None

        for feature in partner_feature:
            if feature['name'] == 'Unbound ASA':
                unbound_asa_data = feature['feature_positions'][0]['values']
            elif feature['name'] == 'Bound ASA':
                bound_asa_data = feature['feature_positions'][0]['values']

        if unbound_asa_data is not None and bound_asa_data is not None:
            table_data = []
            for i in range(len(unbound_asa_data)):
                residue_pos = i + 1
                unbound_asa = unbound_asa_data[i]
                bound_asa = bound_asa_data[i]
                asa_change = unbound_asa - bound_asa
                table_data.append(
                    [residue_pos, unbound_asa, bound_asa, asa_change])

            result[entity_id] = {
                'asym_id': asym_id,
                'table_data': table_data
            }

    return result
