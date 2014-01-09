#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Scripts to convert project data from the French AFD website to the 
# IATI-XML format.

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
#from xml.etree.cElementTree import Element, ElementTree
import urllib2
import os
import unicodecsv
from datetime import datetime
from lib import frhelpers

CSV_FILE = "source/projects.csv"
LOCATIONS_CSV = 'source/projects-locations.csv'
DOCUMENTS_CSV = 'source/projects-documents.csv'
SECTORS_CSV = 'lib/french_dac_codes.csv'

# Basic data setup
reporting_org = u'Minist\xe8re des Affaires \xe9trang\xe8res'
reporting_org_id = u"FR-6"
reporting_org_type = u"10"

def download_data():
    regions = {'MULTI-PAYS': '998'}

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

    def getDocuments():
        documents = []
        docs_file = open(DOCUMENTS_CSV)
        docs_data = unicodecsv.DictReader(docs_file)
        for document in docs_data:
            documents.append((
                document['Standard activity identifier'][0:7], document['Activity Documents']
            ))
        return dict(documents)

    documents = getDocuments()

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
        locations = []
        locations_file = open(LOCATIONS_CSV)
        locations_data = unicodecsv.DictReader(locations_file)
        for location in locations_data:
            locations.append((
                location['Champs'], {'location': location['Sub-national Geographic Location'].strip(), 
                                     'longitude': location['Longitude'], 
                                     'latitude': location['Latitude']}
            ))
        return dictMaker(locations)

    locations = getLocations()

    def correctCountry(name):
        countries = frhelpers.AFD_COUNTRIES
        return countries[name]

    def getSectorName(sector):
        try:
            return DACsectors[sector]
        except Exception:
            return "#####"

    def getCICIDSectorCode(sector):
        return frhelpers.CICID_SECTORS[sector]

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
            return statuses[mappings[status]]

    def getExtendingOrg(org, typ):
        if (type(org) != list):
            org=org.strip().encode('utf-8').lower()
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

        org=org.strip().encode('utf-8').lower()
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
            lcoords = Element("coordinates")
            lcoords.set("latitude", location["latitude"])
            lcoords.set("longitude", location["longitude"])
            # This should probably be set for each location, but they seem
            # to mostly refer to towns etc.
            lcoords.set("precision", "3")
            l.append(lname)
            l.append(lcoords)
            activity.append(l)
        return activity

    def getIATIIdentifier(row):
        if (row["Other activity identifiers"].strip() != ""):
            return row["Other activity identifiers"].replace(" ","")
        else:
            return "ML-"+row["Champs "][7:]

    def getFinanceType(name, type):
        financetypes = frhelpers.FINANCETYPES
        return financetypes[name][type]

    def makeDocuments(row, activity):
        # If it's an AFD project, look to see if there is a related
        # AFD project in the documents file
        if row["Reporting Organisation"] == 'AFD':
            projectid = getIATIIdentifier(row)
            doc_url = ""
            try:
                doc_url = documents[projectid]
            except KeyError:
                try:
                    doc_url = documents[projectid[0:7]]
                except KeyError:
                    pass
            except KeyError:
                pass
            if doc_url != "":
                document_link = Element("document-link")
                document_link.set("url", doc_url)
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

    def makeResults(row, activity):

        def _resulttype(r):
            if r.startswith(u"Résultat"):
                return "2"
            else:
                return "1"
        
        res_headers = [u'Résultat attendue 1',
                         u'Résultat attendue 2',
                         u'Résultat attendue 3',
                         u'Résultat attendue 4',
                         u'Résultat attendue 5']

        real_headers = [u'Réalisation attendue 1',
                         u'Réalisation attendue 2',
                         u'Réalisation attendue 3',
                         u'Réalisation attendue 4',
                         u'Réalisation attendue 5']
        count = 0

        for r in real_headers:
            if row[r] != "":
                if count == 0:
                    result = Element("result")
                    result.set("type", "1")
                    result_title = Element("title")
                    result_title.text = u"Réalisations"
                    result.append(result_title)        
                    activity.append(result)
                indicator = Element("indicator")
                result.append(indicator)
                indicatortitle = Element("title")
                indicatortitle.text = row[r]
                indicatorperiod = Element("period")
                indicatorperiodstart = Element("period-start")
                indicatorperiodstart.text = makeISO(row["Activity Dates (Start Date)"])
                indicator.append(indicatorperiodstart)
                indicatorperiodend = Element("period-end")
                indicatorperiodend.text = makeISO(row[u"Échéance "+r])
                indicator.append(indicatorperiod)
                indicatorperiod.append(indicatorperiodstart)
                indicatorperiod.append(indicatorperiodend)
                indicator.append(indicatortitle)
                count+=1

        count = 0
        for r in res_headers:
            if row[r] != "":
                if count == 0:
                    result = Element("result")
                    result.set("type", "2")
                    result_title = Element("title")
                    result_title.text = u"Résultats"
                    result.append(result_title)        
                    activity.append(result)
                indicator = Element("indicator")
                result.append(indicator)
                indicatortitle = Element("title")
                indicatortitle.text = row[r]
                indicatorperiod = Element("period")
                indicatorperiodstart = Element("period-start")
                indicatorperiodstart.text = makeISO(row["Activity Dates (Start Date)"])
                indicator.append(indicatorperiodstart)
                indicatorperiodend = Element("period-end")
                indicatorperiodend.text = makeISO(row[u"Échéance "+r])
                indicator.append(indicatorperiod)
                indicatorperiod.append(indicatorperiodstart)
                indicatorperiod.append(indicatorperiodend)
                indicator.append(indicatortitle)
                count+=1

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
        
    def write_project(doc, row):
        #FIXME: currently excludes all activities with no project ID
        if row["Champs "] == "":
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

        avancement = SubElement(activity, "{http://data.gouv.fr}avancement")
        avancement.text = row["Etat d'avancement"]

        beneficiaires = SubElement(activity, "{http://data.gouv.fr}beneficiaires")
        beneficiaires.text = row[u"Bénéficiaires finaux"]

        cofinancement = SubElement(activity, "{http://data.gouv.fr}cofinancement")
        cofinancement.text = row[u"Cofinancement"]

        iati_identifier = Element("iati-identifier")
        iati_identifier.text = getExtendingOrg(row["Reporting Organisation"], "id")+"-"+getIATIIdentifier(row)
        activity.append(iati_identifier)

        activity_status = Element("activity-status")
        activity_status.set('code', getStatus(row["Activity Status"], 'code'))
        activity_status.text = getStatus(row["Activity Status"], 'text')
        activity.append(activity_status)

        start_date = Element("activity-date")
        start_date.set('type', 'start-planned')
        start_date.set('iso-date', makeISO(row["Activity Dates (Start Date)"]))
        activity.append(start_date)

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
        aid_type.set("code", row["Default Aid Type"])
        activity.append(aid_type)

        recipient_country = Element("recipient-country")
        recipient_country.set('code', "ML")
        recipient_country.text = "Mali"
        activity.append(recipient_country)

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

        """
        finance_type = Element("default-finance-type")
        finance_type.set("code", getFinanceType(row["funding_type"], 'code'))
        finance_type.text = getFinanceType(row["funding_type"], 'text')
        activity.append(finance_type)
        """

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

        activity = makeLocations(row["Champs "], locations, activity)

        """
        activity_website = Element("activity-website")
        activity_website.text = "http://www.afd.fr/base-projets/consulterProjet.action?idProjet="+row["id"]
        activity.append(activity_website)
        """

        activity = makeDocuments(row, activity)

        activity = makeResults(row, activity)

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

    try:
        print "Starting up ..."
        print "Importing projects data..."

        csv_file = open(CSV_FILE)
        csv_data = unicodecsv.DictReader(csv_file)
        print csv_data.fieldnames

        print "Imported projects data, generating activities..."


        NSMAP = {"fr" : 'http://data.gouv.fr'}

        doc = Element('iati-activities', 
                       nsmap = NSMAP)
        doc.set("version", "1.03")
        current_datetime = datetime.now().replace(microsecond=0).isoformat()
        doc.set("generated-datetime",current_datetime)

        for row in csv_data:
            write_project(doc, row)

        XMLfilename = 'fr-ML.xml'
        print "Writing activities..."

        # TODO: Allow this to be an option on the command line.
        #doc=removeDuplicates(doc)
        doc = ElementTree(doc)
        doc.write(XMLfilename,encoding='utf-8', xml_declaration=True)
        #print "Segmenting files..."
        #prefix = 'afd'
        #output_directory = os.path.realpath('afd')+'/'
        #iatisegmenter.segment_file(prefix, XMLfilename, output_directory)
        print "Done"

    except urllib2.HTTPError, e:
        print "Error %s" % str(e)

download_data()
