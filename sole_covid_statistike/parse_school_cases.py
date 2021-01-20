#!/usr/bin/env python

"""
  Prepare daily covid-19 case summaries for schools
"""

import codecs
import json
import csv


def parse_api(filename):
    header = [
        "date",
        "cases.confirmed",
        "cases.confirmed.todate",
        "cases.active",
        "cases.closed.todate",
        "quarantine.confirmed",
        "quarantine.confirmed.todate",
        "quarantine.active",
        "quarantine.closed",
    ]
    rows = []
    rows.append(header)

    with codecs.open(filename, "r", "utf-8") as f:
        j = json.loads(f.read())

    updates = j[1:]

    cases_confirmed_todate = 0
    quarantines_confirmed_todate = 0
    for u in updates:
        cases_confirmed = (
            u["ucenci_okuzbe_nove"]["Osnovna_sola"]
            + u["ucenci_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
            + u["zaposleni_okuzbe_nove"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_nove"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        cases_confirmed_todate += cases_confirmed
        cases_active = (
            u["ucenci_okuzbe_aktivne"]["Osnovna_sola"]
            + u["ucenci_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
            + u["zaposleni_okuzbe_aktivne"]["Osnovna_sola"]
            + u["zaposleni_okuzbe_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        quarantines_confirmed = (
            u["ucenci_v_karanteni_novi"]["Osnovna_sola"]
            + u["ucenci_v_karanteni_novi"]["Osnovna_sola_s_prilagojenim_programom"]
        )
        quarantines_confirmed_todate += quarantines_confirmed
        quarantines_active = (
            u["ucenci_v_karanteni_aktivne"]["Osnovna_sola"]
            + u["ucenci_v_karanteni_aktivne"]["Osnovna_sola_s_prilagojenim_programom"]
        )

        rows.append(
            [
                "{}-{}-{}".format(u["year"], u["month"], u["day"]),
                cases_confirmed,
                cases_confirmed_todate,
                cases_active,
                cases_confirmed_todate - cases_active,
                quarantines_confirmed,
                quarantines_confirmed_todate,
                quarantines_active,
                quarantines_confirmed_todate - quarantines_active,
            ]
        )

    with codecs.open("schools-cases.csv", "w", "utf-8") as f:
        csvwriter = csv.writer(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        csvwriter.writerows(rows)


if __name__ == "__main__":
    parse_api("mizsdata/api.json")
