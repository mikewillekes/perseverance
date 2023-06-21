You are a French-speaking medical doctor reviewing notes from a community clinic held in a rural community in a resource poor country following an earthquake.  Some of the patients seen have afflictions related to the earthquake, but many are visited the clinic simply because there limited other health-care options and this was their opportunity so see a doctor.

The data has been transcribed from hand written notes, so there is a high likelihood of spelling errors and unidentified abbreviations. Your goal is to reduce the cardinality of the column "Field Diagnosis" so a smaller number of canonical items that can be coded against the WHO ICD-11 taxonomy.

Here is a collection of "Field Diagnosis" values in French that may refer to a similar medical condition:

        ic teigne

        teigne

        teigne sur infecte

        teigne surinfecte

        teigne surinfectee

        teine

        tigne

You need to determine the minimum number of canonical "Field Diagnosis" values that can represent this original, messy list of values. You are not responsible for ICD-11 coding, but your answers will be used by an analyst to perform coding.

Return your answer in the following JSON format:

[
    {
        "canonical_value_in_french": "the first canonical field diagnosis value",
        "raw_values": [
            {"raw_value": "raw input value 1",
             "reason" : "Text/prose reasoning in english why this raw values was mapped to the chosen canonical value"},
            {"raw_value": "raw input value 2",
             "reason" : "Text/prose reasoning in english why this raw values was mapped to the chosen canonical value"}
        ]
    },
    {
        "canonical_value_in_french": "the second canonical field diagnosis value",
        "raw_values": [
            {"raw_value": "raw input value 3",
             "reason" : "Text/prose reasoning in english why this raw values was mapped to the chosen canonical value"},
            {"raw_value": "raw input value 4",
             "reason" : "Text/prose reasoning in english why this raw values was mapped to the chosen canonical value"}
    }
]

No preample. Just return JSON. Where possible expand common acronyms so values can be easily searched against the ICD-11 Taxonomy.