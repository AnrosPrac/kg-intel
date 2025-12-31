QUERIES = [
    "Arshad Azeez M",
    "Sidhi Labs",
    "Lumetrix sidhi",
    "Engdraft sidhi"
]

CONFIDENCE_RULES = {
    "HIGH": "kg_id_present",
    "MEDIUM": "result_without_id",
    "LOW": "no_result"
}

ENTITY_GRAPH = {
    "parent": {
        "name": "Sidhi",
        "aliases": [
            "Sidhi Ecosystem",
            "sidhi.xyz"
        ]
    },
    "founder": {
        "name": "Arshad Azeez M",
        "aliases": [
            "Arshad Azeez"
        ]
    },
    "children": [
        {
            "name": "Lumetrix",
            "aliases": []
        }
    ]
}
