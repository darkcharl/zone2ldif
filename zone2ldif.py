#!/usr/bin/env python

"""
    Simple bind zone file to LDIF converter

    Author: Robert Barabas

"""

import os
import sys
import dns.zone
from optparse import OptionParser
from dns.exception import DNSException
from dns.rdatatype import *
from dns.rdataclass import *

usage = "{0} [options] zonefile domain ipadomain".format(sys.argv[0])

def parseargs():
    """ Parses command line arguments """
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--debug", default=False, action="store_true",
        help="enables debug mode")
    (opts, args) = parser.parse_args()
    return (opts, args)


def main():
    """ Loads and parses zone file and converts its data to LDIF """
    (opts, args) = parseargs()
    if len(args) != 3:
        print usage
        sys.exit(1)
    zone_file = args[0]
    domain = args[1]
    ipadomain = args[2]
    ldif_file = '{0}.ldif'.format(zone_file)
    ipadcs = ['dc={0}'.format(x) for x in ipadomain.split('.')]
    ipadomain_ldap = ','.join(ipadcs)
    if opts.debug:
        print(" [D] using zone file {0}".format(zone_file))
        print(" [D] domain set to {0}".format(domain))
    try:
        zone = dns.zone.from_file(zone_file, domain)
        ldif = {}
        try:
            f = open(ldif_file, 'w')
        except e:
            print e.__class__, e
        """ Iterate through each "node" and add attributes """
        for name, node in zone.nodes.items():
            if opts.debug:
                print(" [D] found node: {0}".format(name))
            ldif[name] = []
            ldif[name].append('# {0}, {1}, dns, {2}'.format(
                              name, domain, ipadomain))
            ldif[name].append('dn: idnsname={0},idnsname={1},cn=dns,{2}'.format(
                              name, domain, ipadomain_ldap))
            ldif[name].append('objectClass: top')
            ldif[name].append('objectClass: idnsrecord')
            """ rdatasets: RR types """
            rdatasets = node.rdatasets
            """ rdataset: records for a given RR type """
            for rdataset in rdatasets:
                rrtype = rdataset.rdtype
                """ rdata: a given RR record """
                for rdata in rdataset:
                    if opts.debug:
                        print(" [D] found record type:"
                              " {0}".format(dns.rdatatype.to_text(rrtype)))
                    if rrtype == SOA:
                        """ SOA specific fields """
                        ldif[name].append('objectClass: idnszone')
                        ldif[name].append('idnsSOAexpire: {0}'.format(rdata.expire))
                        ldif[name].append('idnsSOAminimum: {0}'.format(rdata.minimum))
                        ldif[name].append('idnsSOAmName: {0}'.format(rdata.mname))
                        ldif[name].append('idnsSOArefresh: {0}'.format(rdata.refresh))
                        ldif[name].append('idnsSOAretry: {0}'.format(rdata.retry))
                        ldif[name].append('idnsSOArName: {0}'.format(rdata.rname))
                        ldif[name].append('idnsSOAserial: {0}'.format(rdata.serial))
                    if rrtype == NS:
                        """ NS specific fields """
                        ldif[name].append('nSRecord: {0}'.format(rdata.target))
                        ldif[name].append('idnsName: {0}'.format(name))
                    if rrtype == MX:
                        """ MX specific fields """
                        ldif[name].append('mXRecord: {0} {1}'.format(rdata.preference,
                                                                     rdata.exchange))
                        ldif[name].append('idnsName: {0}'.format(name))
                    if rrtype == A:
                        """ A specific fields """
                        ldif[name].append('aRecord: {0}'.format(rdata.address))
                        ldif[name].append('idnsName: {0}'.format(name))
                    if rrtype == CNAME:
                        """ CNAME specific fields """
                        ldif[name].append('cNAMERecord: {0}'.format(rdata.target))
                        ldif[name].append('idnsName: {0}'.format(name))
                    if rrtype == PTR:
                        """ PTR specific fields """
                        ldif[name].append('pTRRecord: {0}'.format(rdata.target))
                        ldif[name].append('idnsName: {0}'.format(name))
            ldif_obj = "\n".join(ldif[name])
            if opts.debug:
                print(" [D] found resource record: ")
                print("{0}\n".format(ldif_obj))
            """ Write object to file """
            f.write("{0}\n\n".format(ldif_obj))
        f.close()
    except DNSException, e:
        print e.__class__, e


if __name__ == "__main__":
    main()


