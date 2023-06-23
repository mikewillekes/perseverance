from datetime import datetime
from serde import serialize, deserialize
from serde.json import from_json, to_json
from dataclasses import dataclass
from typing import List

@deserialize
@serialize
@dataclass
class GPTCleanedDiagnosis:
    raw_field_diagnosis_french: str
    clean_field_diagnosis_french: str


@deserialize
@serialize
@dataclass
class Dossier:
    id: str
    date: datetime
    raw_symptoms: str
    raw_diagnoses: str
    symptoms: List[str]
    diagnoses: List[str]
    gpt_cleaned_diagnoses: List[GPTCleanedDiagnosis]


def load_dossiers(filename):
    # Deserialized from Jsonl file
    dossiers = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            dossiers.append(from_json(Dossier, line.strip()))
    return dossiers


def save_dossiers(filename, dossiers):
    # Serialize to json string & append newline
    lines = []
    for m in dossiers:
        lines.append(to_json(m) + '\n')
    # Save to Jsonl file
    open(filename, 'w').writelines(lines)


def load_gpt_cleaned_diagnoses(filename):
    # Deserialized from Jsonl file
    diagnoses = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            diagnoses.append(from_json(GPTCleanedDiagnosis, line.strip()))
    return diagnoses


def save_gpt_cleaned_diagnoses(filename, diagnoses):
    # Serialize to json string & append newline
    lines = []
    for m in diagnoses:
        lines.append(to_json(m) + '\n')
    # Save to Jsonl file
    open(filename, 'a').writelines(lines)