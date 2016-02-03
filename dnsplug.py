## @package dnsplug
# Provide a higher level interface to pydns or dnspython (or other provider).
# NOT RELEASED: this is a proposed API and implementation.
# Goals - work with both pydns and dnspython (and possibly other libraries)
# at a simplied level.
# TODO:
# 1. map exceptions to common dnsplug.DNSError exception (with
#    original exception saved as a member).
# 2. include dict based implementation (handy for test suites)
# 3. move implementations to subpackages to enable autoselect on first call.

## Maximum number of CNAME records to follow
MAX_CNAME = 10

## Lookup DNS records by label and RR type.
# The response can include records of other types that the DNS
# server thinks we might need.  FIXME: empty result
# could mean NXDOMAIN or NOANSWER.
# @param name the DNS label to lookup
# @param qtype the name of the DNS RR type to lookup
# @param tcpfallback if False, raise exception instead of TCP fallback
# @return a list of ((name,type),data) tuples
def DNSLookup(name, qtype, tcpfallback=True, timeout=30):
    raise NotImplementedError('No supported dns library found')

class Session(object):
  """A Session object has a simple cache with no TTL that is valid
   for a single "session", for example an SMTP conversation."""
  def __init__(self):
    self.cache = {}

  ## Additional DNS RRs we can safely cache.
  # We have to be careful which additional DNS RRs we cache.  For
  # instance, PTR records are controlled by the connecting IP, and they
  # could poison our local cache with bogus A and MX records.  
  # Each entry is a tuple of (query_type,rr_type).  So for instance,
  # the entry ('MX','A') says it is safe (for milter purposes) to cache
  # any 'A' RRs found in an 'MX' query.
  SAFE2CACHE = frozenset((
    ('MX','MX'), ('MX','A'),
    ('CNAME','CNAME'), ('CNAME','A'),
    ('A','A'),
    ('AAAA','AAAA'),
    ('PTR','PTR'),
    ('NS','NS'), ('NS','A'),
    ('TXT','TXT'),
    ('SPF','SPF')
  ))

  ## Cached DNS lookup.
  # @param name the DNS label to query
  # @param qtype the query type, e.g. 'A'
  # @param cnames tracks CNAMES already followed in recursive calls
  def dns(self, name, qtype, cnames=None):
    """DNS query.

    If the result is in cache, return that.  Otherwise pull the
    result from DNS, and cache ALL answers, so additional info
    is available for further queries later.

    CNAMEs are followed.

    If there is no data, [] is returned.

    pre: qtype in ['A', 'AAAA', 'MX', 'PTR', 'TXT', 'SPF']
    post: isinstance(__return__, types.ListType)
    """
    result = self.cache.get( (name, qtype) )
    cname = None

    if not result:
        safe2cache = Session.SAFE2CACHE
        for k, v in DNSLookup(name, qtype):
            if k == (name, 'CNAME'):
                cname = v
            if (qtype,k[1]) in safe2cache:
                self.cache.setdefault(k, []).append(v)
        result = self.cache.get( (name, qtype), [])
    if not result and cname:
        if not cnames:
            cnames = {}
        elif len(cnames) >= MAX_CNAME:
            #return result    # if too many == NX_DOMAIN
            raise DNSError('Length of CNAME chain exceeds %d' % MAX_CNAME)
        cnames[name] = cname
        if cname in cnames:
            raise DNSError, 'CNAME loop'
        result = self.dns(cname, qtype, cnames=cnames)
    return result

def DNSLookup_pydns(name, qtype, tcpfallback=True, timeout=30):
    try:
	# FIXME: To be thread safe, we create a fresh DnsRequest with
	# each call.  It would be more efficient to reuse
	# a req object stored in a Session.
        req = DNS.DnsRequest(name, qtype=qtype, timeout=timeout)
        resp = req.req()
        #resp.show()
        # key k: ('wayforward.net', 'A'), value v
        # FIXME: pydns returns AAAA RR as 16 byte binary string, but
        # A RR as dotted quad.  For consistency, this driver should
        # return both as binary string.
        #
        if resp.header['tc'] == True:
          if not tcpfallback:
              raise DNS.DNSError, 'DNS: Truncated UDP Reply, SPF records should fit in a UDP packet'
          try:
              req = DNS.DnsRequest(name, qtype=qtype, protocol='tcp',
                        timeout=timeout)
              resp = req.req()
          except DNS.DNSError, x:
              raise DNS.DNSError, 'TCP Fallback error: ' + str(x)
        return [((a['name'], a['typename']), a['data']) for a in resp.answers]
    except IOError, x:
        raise DNS.DNSError, 'DNS: ' + str(x)

def DNSLookup_dnspython(name,qtype,tcpfallback=True,timeout=30):
  retVal = []
  try:
    # FIXME: how to disable TCP fallback in dnspython if not tcpfallback?
    answers = dns.resolver.query(name, qtype)
    for rdata in answers:
      if qtype == 'A' or qtype == 'AAAA':
        retVal.append(((name, qtype), rdata.address))
      elif qtype == 'MX':
        retVal.append(((name, qtype), (rdata.preference, rdata.exchange)))
      elif qtype == 'PTR':
        retVal.append(((name, qtype), rdata.target.to_text(True)))
      elif qtype == 'TXT' or qtype == 'SPF':
        retVal.append(((name, qtype), rdata.strings))
  except dns.resolver.NoAnswer:
    pass
  except dns.resolver.NXDOMAIN:
    pass
  return retVal

try:
    # prefer dnspython (the more complete library)
    import dns
    import dns.resolver  # http://www.dnspython.org
    import dns.exception

    if not hasattr(dns.rdatatype,'SPF'):
      # patch in type99 support
      dns.rdatatype.SPF = 99
      dns.rdatatype._by_text['SPF'] = dns.rdatatype.SPF

    DNSLookup = DNSLookup_dnspython
except:
    import DNS    # http://pydns.sourceforge.net

    if not hasattr(DNS.Type, 'SPF'):
        # patch in type99 support
        DNS.Type.SPF = 99
        DNS.Type.typemap[99] = 'SPF'
        DNS.Lib.RRunpacker.getSPFdata = DNS.Lib.RRunpacker.getTXTdata

    # Fails on Mac OS X? Add domain to /etc/resolv.conf
    DNS.DiscoverNameServers()

    DNSLookup = DNSLookup_pydns

if __name__ == '__main__':
  import sys
  s = Session()
  for n,t in zip(*[iter(sys.argv[1:])]*2):
    print n,t
    print s.dns(n,t)
