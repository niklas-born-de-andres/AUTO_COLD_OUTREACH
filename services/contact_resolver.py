#Loads both CSVs into memory on startup as lists of dicts for simple lookup
#If contact list size becomes a problem,  the data can be indexed on load using a dictionary
#Contact matches are case insensitive


import csv
import os

class ContactResolver:

    def __init__(self):
        self.contacts = self._load_csv("data/contacts.csv")
        self.team_members = self._load_csv("data/team.csv")

    def _load_csv(self, filepath: str) -> list:
        #csv saved with UTF8
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f, delimiter=";"))

    def get_contact(self, first_name: str, last_name: str) -> dict:

        for row in self.contacts:
            if (row["first_name"].lower() == first_name.lower() and
                row["last_name"].lower() == last_name.lower()):

                return {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "company": row["company"],
                    "notes": row.get("notes", "")
                }
        raise ValueError(f"Contact '{first_name} {last_name}' not found.")


    def get_team_member(self, name: str) -> dict:

        for row in self.team_members:
            if row["name"].lower() == name.lower():
                return {
                    "name": row["name"],
                    "email": row["email"],
                    "role": row["role"]
                }
        raise ValueError(f"Team member '{name}' not found.")