#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Scripts to convert project data from a French-specific XLSX template to
# the IATI-XML format.

# MIT Licensed
#
# Copyright (c) 2013 Mark Brough, Publish What You Fund
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from lxml import etree
from lxml.etree import *
import urllib2
import os
import unicodecsv
from datetime import datetime
from lib import frhelpers
from lib import xlsx_to_csv

XLSX_FILE = "source/projects-niger-afd.xlsx"
thisfile_dir = os.path.dirname(os.path.abspath(__file__))
SECTORS_CSV = os.path.join(thisfile_dir, 'lib/french_dac_codes.csv')
COUNTRIES_CSV = os.path.join(thisfile_dir, 'lib/french_country_region_codes.csv')

# Basic data setup
reporting_org = u'Minist\xe8re des Affaires \xe9trang\xe8res'
reporting_org_id = u"FR-6"
reporting_org_type = u"10"

parent_activities = {}

def convert(input_filename, input_data, XMLfilename='fr-ML.xml'):
    XMLfilename = os.path.join(thisfile_dir, 'static/data/', XMLfilename)
    print XMLfilename

    def getDACSectors():
        DACsectors = []
        sectors_file = open(SECTORS_CSV)
        sectors_data = unicodecsv.DictReader(sectors_file)
        for sector in sectors_data:
            DACsectors.append((
                sector['DAC3DAC5'], sector['TEXT'].strip()
            ))
        return dict(DACsectors)

    DACsectors = getDACSectors()

    def getCountries():
        countries = []
        countries_file = open(COUNTRIES_CSV)
        countries_data = unicodecsv.DictReader(countries_file)
        for country in countries_data:
            countries.append((
            country['name'], {'code': country['code'],
                              'type': country['type'],
                             }
            ))
        return dict(countries)

    countries = getCountries()

    def dictMaker(locations):
        out = {}
        for location in locations:
            try:
                out[location[0]].append(location[1])
            except KeyError:
                out[location[0]] = []
                out[location[0]].append(location[1])
        return out                        

    def getLocations():
        coords_data = xlsx_to_csv.getDataFromFile(input_filename, input_data, u"LocationCoords")
        coords = dict([ (row['LookupName'], row) for row in coords_data])

        locations_data = xlsx_to_csv.getDataFromFile(input_filename, input_data, u"Locations")

        locations = []
        for location in locations_data:
            locations.append((
                location['Champs'], {'location': location['Sub-national Geographic Location'].strip(), 
                                     'longitude': coords[location['LookupLocation']]['Long'], 
                                     'latitude': coords[location['LookupLocation']]['Lat']}
            ))
        return dictMaker(locations)

    def correctCountry(name):
        countries = frhelpers.AFD_COUNTRIES
        return countries[name]

    def getSectorName(sector):
        try:
            return DACsectors[sector]
        except Exception:
            return "#####"

    def getCICIDSectorCode(sector):
        return frhelpers.CICID_SECTORS[sector.strip()]

    def checkIfRegion(name):
        if name in regions:
            return True
        return False

    def makeISO(date):
        if len(date)<10:
            return ""
        return date[6:10]+"-"+date[3:5]+"-"+date[0:2]

    def getStatus(status, type):
        status=status.strip().encode('utf-8').lower()
        mappings = frhelpers.FR_STATUSES
        statuses = frhelpers.STATUSCODES
        if type =='code':
            return mappings[status]
        else:
            return unicode(statuses[mappings[status]].decode("utf-8"))

    def getExtendingOrg(org, typ):
        if (type(org) != list):
            org=org.strip().lower()
        mappings = frhelpers.FR_ORGS
        codes = frhelpers.FR_ORGS_CODES
        if typ =='id':
            return mappings[org]
        else:
            return codes[mappings[org]]

    def makeExtendingOrg(org, activity):
        def _makeEO(org):
            extending_org = Element("participating-org")
            extending_org.set("role", "Extending")
            extending_org.set("ref", getExtendingOrg(org, "id"))
            extending_org.set("type", "10")
            extending_org.text = getExtendingOrg(org, "text")
            activity.append(extending_org)

        org=org.strip().lower()
        if org=="scac et afd":
            for o in ['scac', 'afd']:
                _makeEO(o)
        else:
            _makeEO(org)

        return activity

    def makeLocations(champs, locations, activity):
        for location in locations[champs.strip()]:
            l = Element("location")
            lname = Element("name")
            lname.text = location["location"]
            if ((location["latitude"] != "") and 
                    (location["latitude"] != "0")):
                lcoords = Element("coordinates")
                lcoords.set("latitude", location["latitude"])
                lcoords.set("longitude", location["longitude"])
                # This should probably be set for each location, but they seem
                # to mostly refer to towns etc.
                lcoords.set("precision", "3")
                l.append(lcoords)
            l.append(lname)
            activity.append(l)
        return activity

    def getIATIIdentifier(row):
        if (row["Project code"].strip() != ""):
            return row["Project code"].replace(" ","")
        else:
            return getCountryRegionCode(row["Country / Region"])+"-"+row["Champs"][7:]

    def getFinanceType(name, type):
        financetypes = frhelpers.FINANCETYPES
        return unicode(financetypes[name][type].decode("utf-8"))

    def getAidType(name, type):
        aidtypes = frhelpers.AIDTYPES
        return unicode(aidtypes[name][type].decode("utf-8"))

    def makeDocuments(row, activity):
        # If it's an AFD project, look to see if there is a related
        # AFD project in the documents file
        if row["Activity Documents"] != "":
            document_link = Element("document-link")
            document_link.set("url", row["Activity Documents"])
            document_link.set("format", "text/html")
            document_title = Element("title")
            document_title.text = "Projet fiche"
            document_link.append(document_title)
            document_category = Element("category")
            document_category.set("code", "A02")
            document_category.text = "Objectives / Purpose of activity"
            document_link.append(document_category)
            activity.append(document_link)
        return activity

    def removeDuplicates(doc):

        def f7(seq):
            seen = set()
            seen_add = seen.add
            # adds all elements it doesn't know yet to seen and all other to seen_twice
            seen_twice = set( str(x) for x in seq if x in seen or seen_add(x) )
            # turn the set into a list (as requested)
            return list( seen_twice )

        #doc = etree.tostring(doc)
        iati_identifiers = doc.xpath('//iati-identifier/text()')
        duplicates = f7(iati_identifiers)

        for did in duplicates:
            print "Removing all activities with duplicated identifier", did
            for duplicate in (doc.xpath("//iati-identifier[text()='%s']" % did)):
                duplicate.getparent().remove(duplicate)
        return doc

    def getCountryRegionCode(countryregion):
        try:
            return countries[countryregion]['code']
        except KeyError:
            return 'NULL'

    def getCountryRegion(activity, countryregion):
        try:
            item = countries[countryregion]
            if item['type'] == 'country':
                cou = Element("recipient-country")
                cou.set("code", item['code'])
                cou.text = countryregion
                activity.append(cou)                 
            else:
                reg = Element("recipient-region")
                reg.set("code", item['code'])
                reg.text = countryregion
                activity.append(reg) 
        except KeyError:
            reg = Element("recipient-region")
            reg.set("code", "998")
            reg.text = "Pays en développement, non spécifié"
            activity.append(reg)
        return activity

    def write_parent_activity(doc, parent_activity):
        activity = Element("iati-activity")
        activity.set("default-currency", "EUR")
        activity.set("last-updated-datetime", makeISO(row[u"Date de mise \xe0 jour de la fiche"])+"T00:00:00")
        activity.set("hierarchy", "1")
        doc.insert(0, activity)

        iati_identifier = Element("iati-identifier")
        iati_identifier.text = parent_activity[0]
        activity.append(iati_identifier)

        title = Element("title")
        title.text = parent_activity[1]["row"]["Activity Title"]
        activity.append(title)

        for child in parent_activity[1]["children"]:
            rel = Element("related-activity")
            rel.set("type", "2")
            rel.set("ref", child)
            activity.append(rel)
        
    def write_project(doc, row):
        #FIXME: currently excludes all activities with no project ID

        if row["Champs"] == "":
            return
        
        activity = Element("iati-activity")
        activity.set("default-currency", "EUR")
        activity.set("last-updated-datetime", makeISO(row[u"Date de mise \xe0 jour de la fiche"])+"T00:00:00")
        doc.append(activity)

        rep_org = Element("reporting-org")
        rep_org.set("ref", getExtendingOrg(row["Reporting Organisation"], "id"))
        rep_org.set("type", "10")
        rep_org.text = getExtendingOrg(row["Reporting Organisation"], "text")
        activity.append(rep_org)

        title = Element("title")
        title.text = row["Activity Title"]
        activity.append(title)

        description = Element("description")
        description.text = row["Activity Long Description"]
        activity.append(description)

        iati_identifier = Element("iati-identifier")
        activity_iati_identifier = getExtendingOrg(row["Reporting Organisation"], "id")+"-"+getIATIIdentifier(row)
        iati_identifier.text = activity_iati_identifier
        activity.append(iati_identifier)

        activity_status = Element("activity-status")
        activity_status.set('code', getStatus(row["Activity Status"], 'code'))
        activity_status.text = getStatus(row["Activity Status"], 'text')
        activity.append(activity_status)

        start_date = Element("activity-date")
        start_date.set('type', 'start-planned')
        start_date.set('iso-date', makeISO(row["Activity Dates (Start Date)"]))
        activity.append(start_date)

        if (row["Activity Dates (End Date)"] != ""):
            end_date = Element("activity-date")
            end_date.set('type', 'end-planned')
            end_date.set('iso-date', makeISO(row["Activity Dates (End Date)"]))
            activity.append(end_date)

        collab_type = Element("collaboration-type")
        collab_type.set("code", "1")
        collab_type.text = u"Bilatéral"
        activity.append(collab_type)
        
        flow_type = Element("default-flow-type")
        flow_type.set("code", "10")
        flow_type.text=u"APD"
        activity.append(flow_type)
        
        tied_status = Element("default-tied-status")
        tied_status.set("code", "5")
        tied_status.text=u"Aide déliée"
        activity.append(tied_status)
        
        aid_type = Element("default-aid-type")
        aid_type.set("code", getAidType(row["Default Aid Type"], 'code'))
        aid_type.text = getAidType(row["Default Aid Type"], 'text')
        activity.append(aid_type)

        activity = getCountryRegion(activity, row["Country / Region"])

        funding_org = Element("participating-org")
        funding_org.set("role", "Funding")
        funding_org.set("ref", "FR")
        funding_org.set("type", "10")
        funding_org.text = "France"
        activity.append(funding_org)

        activity = makeExtendingOrg(row["Reporting Organisation"], activity)

        implementing_org = Element("participating-org")
        implementing_org.set("role", "Implementing")
        implementing_org.text = row["Participating Organisation (Implementing)"]
        activity.append(implementing_org)

        finance_type = Element("default-finance-type")
        finance_type.set("code", getFinanceType(row["Default Finance Type"], 'code'))
        finance_type.text = getFinanceType(row["Default Finance Type"], 'text')
        activity.append(finance_type)

        sector = Element("sector")
        sector.set("code", row["Sector (DAC CRS)"])
        sector.set("vocabulary", "DAC")
        sector.text = getSectorName(row["Sector (DAC CRS)"])
        activity.append(sector)

        sector = Element("sector")
        sector.set("code", getCICIDSectorCode(row["Sector (Agency specific)"]))
        sector.set("vocabulary", "RO")
        sector.text = row["Sector (Agency specific)"]
        activity.append(sector)

        activity = makeLocations(row["Champs"], locations, activity)

        if row["Activity Website"] != "":
            activity_website = Element("activity-website")
            activity_website.text = row["Activity Website"]
            activity.append(activity_website)

        activity = makeDocuments(row, activity)

        if row["Activity Budget"] != "":
            transaction = Element("transaction")
            activity.append(transaction)
            ttype = Element("transaction-type")
            ttype.set("code", "C")
            ttype.text = "Commitment"
            transaction.append(ttype)

            tvalue = Element("value")
            tvalue.set('value-date', makeISO(row["Activity Dates (Start Date)"]))
            tvalue.text = row["Activity Budget"]
            transaction.append(tvalue)

            tdate = Element("transaction-date")
            tdate.set("iso-date", makeISO(row["Activity Dates (Start Date)"]))
            tdate.text=makeISO(row["Activity Dates (Start Date)"])
            transaction.append(tdate)

        if ((row["Financial transaction (Disbursement & Expenditure)"] != "")
                and (int(float(row["Financial transaction (Disbursement & Expenditure)"])) != 0)):
            disbursement = Element("transaction")
            activity.append(disbursement)
            ttype = Element("transaction-type")
            ttype.set("code", "D")
            ttype.text = "Disbursement"
            disbursement.append(ttype)

            tvalue = Element("value")
            tvalue.set('value-date', makeISO(row["Activity Dates (Start Date)"]))
            tvalue.text = row["Financial transaction (Disbursement & Expenditure)"]
            disbursement.append(tvalue)

            tdate = Element("transaction-date")
            tdate.set("iso-date", datetime.now().date().isoformat())
            tdate.text=datetime.now().date().isoformat()
            disbursement.append(tdate)

        if (row["Parent project code (if applicable)"] != ""):
            activity.set("hierarchy", "2")
            rel = Element("related-activity")
            rel.set("type", "1")
            parent_ref = getExtendingOrg(row["Reporting Organisation"], "id")+"-"+row["Parent project code (if applicable)"]
            rel.set("ref", parent_ref)
            activity.append(rel)
            if not parent_activities.get(parent_ref):
                parent_activities[parent_ref] = {
                    'row': row,
                    'children': []
                }
            parent_activities[parent_ref]['children'].append(activity_iati_identifier)

    print "Starting up ..."
    print "Importing projects data ... (1/4)"

    csv_data = xlsx_to_csv.getDataFromFile(input_filename, input_data, u"Projets")

    print "Imported projects data"
    print "Generating locations ... (2/4)"
    locations = getLocations()

    print "Generated locations"
    print "Generating activities ... (3/4)"

    doc = Element('iati-activities')
    doc.set("version", "1.03")
    current_datetime = datetime.now().replace(microsecond=0).isoformat()
    doc.set("generated-datetime",current_datetime)

    for row in csv_data:
        write_project(doc, row)

    for parent_activity in parent_activities.items():
        write_parent_activity(doc, parent_activity)
	
    print "Generated activities"
    print "Writing activities ... (4/4)"

    doc = ElementTree(doc)
    doc.write(XMLfilename,encoding='utf-8', xml_declaration=True, pretty_print=True)
    print "Done"
    return True

if __name__ == '__main__':
    input_filename = XLSX_FILE
    input_data = open(input_filename).read()
    if convert(input_filename, input_data):
        print "Successfully converted your data"
