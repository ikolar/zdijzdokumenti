#!/usr/bin/env python
"""
    Merge all the dictionaries from
    https://paka3.mss.edus.si/registriweb/default.aspx into one.
"""

import codecs
import csv
from bs4 import BeautifulSoup


def parse_table(filename, code):
    with codecs.open(filename, "r", "windows-1250") as f:
        html = f.read()
    soup = BeautifulSoup(html, features="html.parser")
    rows = soup.table.find_all("tr")

    parsed = []

    if "srednjih šol" not in filename:
        # some places are units (podružnice) for bigger institutions
        # keep track of their main institution (maticni zavod) here
        maticni = None
        for row in rows[1:]:
            cells = row.find_all("td")
            values = list(map(lambda c: c.text.strip("\r\n\t\xa0"), cells))
            values = values[0:12]

            if "vrtcev" in filename or "osnovnih šol." in filename:
                # check if this is a maticni zavod (name will be in bold)
                link = cells[4].find("a")
                strong = link.find("strong")
                if strong:
                    maticni = values
            else:
                maticni = values
            # mark maticni zavod
            values.insert(1, maticni[0])

            parsed.append(values)

    elif (
        "osnovnih šol za otroke s posebnimi potrebami" in filename
        or "glasbenih šol" in filename
    ):
        pass

    elif "srednjih šol." in filename:
        region = None
        previous = None
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 1:
                # special row for the statistical region
                region = cells[0].text.strip("\r\n\t\xa0")
                continue
            elif "ZAVSIF" in cells[0].text:
                # header
                continue
            else:
                values = list(map(lambda c: c.text.strip("\r\n\t\xa0"), cells))
                values.insert(2, region)
                values = values[0:12]

                # mark maticni zavod
                if previous and previous[2] in values[2]:
                    values.insert(1, previous[0])
                else:
                    values.insert(1, "")

                # obcina is missing
                # guess with posta
                values.insert(4, values[7])

                previous = values

                parsed.append(values)

    # postprocessing
    for values in parsed:
        # add zavod type
        values.insert(0, code)

        # add geo placeholders
        values.insert(10, "")  # openstreetmap
        values.insert(11, "")  # Register prostorskih enot - solski okolis

        # prefix url with http if missing
        if values[-1] and "http" not in values[-1].lower():
            values[-1] = "http://" + values[-1]

    return parsed


def getmanualgeo():
    """
    Get a manually prepapred dict() of locations for specific schools.

    key: ZAVSIF, value: SL_ID (GURS RPE SL) or OpenStreetMap URL.
    """

    geo_openstreetmap = {}
    with codecs.open("zavsif_openstreetmap.csv", "r", "utf-8") as f:
        lines = f.read().split("\n")[1:]
        for line in lines:
            (zavid, url) = line.split(";")
            geo_openstreetmap[zavid] = url

    geo_rpe = {}
    with codecs.open("zavsif_rpe.csv", "r", "utf-8") as f:
        lines = f.read().split("\n")[1:]
        for line in lines:
            (zavid, slid, name) = line.split("\t")
            geo_rpe[zavid] = slid

    return geo_openstreetmap, geo_rpe


def merge():
    rows = []
    rows.extend(parse_table("seznam_osnovnih šol.html", "OŠ"))
    rows.extend(parse_table("seznam_vrtcev.html", "vrtec"))
    rows.extend(
        parse_table("seznam_osnovnih šol za otroke s posebnimi potrebami.html", "OŠPP")
    )
    rows.extend(parse_table("seznam_glasbenih šol.html", "GŠ"))
    rows.extend(parse_table("seznam_srednjih šol.html", "SŠ"))
    rows.extend(parse_table("seznam_višjih strokovnih šol.html", "VSŠ"))
    rows.extend(
        parse_table(
            "seznam_zavodov za otroke in mladostnike s posebnimi potrebami.html", "VSŠ"
        )
    )

    # add geo
    geo_openstreetmap, geo_rpe = getmanualgeo()
    for row in rows:
        zavsif = row[1]
        row[10] = geo_openstreetmap.get(zavsif, "").strip(" \n\r")
        row[11] = geo_rpe.get(zavsif, "")

    with codecs.open("dict-schools.csv", "w", "utf-8") as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                "type",
                "zavid",
                "matzavid",
                "maticna",
                "region",
                "municipality",
                "name",
                "address",
                "post",
                "post.office",
                "openstreetmap",
                "slid",
                "phone",
                "fax",
                "email",
                "website",
            ]
        )
        writer.writerows(rows)


if __name__ == "__main__":
    merge()
