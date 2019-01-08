zone2ldif
=========

## Description
Converts a DNS zone file to a LDIF file which can be used to add
that zone into IPA

# Usage:

## Preparation

If you do not have acess to a ISC Bind zone file, i.e. the DNS server is a MS-DNS, you can you dig AXFR to dump the zone. Ensure your IP address is allowed to do zone transfers.

```bash
dig example.com AXFR @dnsserver.example.com > example.com.zone
```
## Convert the zone file to LDIF

```bash
./zone2dyndb-ldif.py example.com.zone example.com "cn=dns, dc=example, dc=com" > example.com.ldif
```

## Import the zone to IPA

Ensure the zone does not exist in IPA, if so, delete it or adjust the LDIF file.

```bash
ldapadd -x -W -D cn="Directory Manager" < example.com.ldif 
```

# Note
This procedure is not supported by Red Hat. However,  as of 2019-01-08, it is working with IPA 4.6.4 delivered with RHEL 7.6.


