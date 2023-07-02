from datetime import datetime
from serde import serialize, deserialize
from serde.json import from_json, to_json
from dataclasses import dataclass
from typing import List

@deserialize
@serialize
@dataclass
class ICDEntity:
    code: str
    title: str
    grouping_depth: int
    is_leaf: bool
    grouping: str
    embeddings: List[float]


def load_icd_entities(filename):
    # Deserialized from Jsonl file
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            yield from_json(ICDEntity, line.strip())

def save_icd_entities(filename, entities):
    # Serialize to json string & append newline
    lines = []
    for e in entities:
        lines.append(to_json(e) + '\n')
    # Save to Jsonl file
    open(filename, 'w').writelines(lines)

def save_icd_entity(filename, entity):
    # Serialize to json string & append newline
    lines = [to_json(entity) + '\n']
    # Save to Jsonl file
    open(filename, 'a').writelines(lines)