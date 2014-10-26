from os.path import dirname, isfile, join
from urllib.parse import urljoin

import xml.etree.ElementTree as ET
import urllib.request        as requests
import hashlib
import sys

__all__ = ['connect', 'statistics', 'device_info', 'pass_hash',
           'file', 'sent_received', 'status']

SERVER = 'http://192.168.1.1'

KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024
TB = 1024 * 1024 * 1024 * 1024

def humanize_size(size):
    size = int(size)
    if MB > size >= KB:
        return format((size/KB), '.2f') + ' KB'
    elif GB > size >= MB:
        return format((size/MB), '.2f') + ' MB'
    elif TB > size >= GB:
        return format((size/GB), '.2f') + ' GB'
    elif size >= TB:
        return format((size/TB), '.2f') + ' TB'
    else:
        return str(size) + ' B'

def humanize_time(time, sep=':'):
    final_time = ''
    times = int(time)
    
    #handle hour display
    hours = int(times / 3600)
    if (hours > 9):
        final_time += str(hours) + sep
    elif (hours >= 0):
        final_time += '0' + str(hours) + sep
    times = times - hours * 3600

    #handle minute display
    minutes = int(times / 60)
    if (minutes > 9):
        final_time += str(minutes) + sep
    elif (minutes > 0):
        final_time += '0' + str(minutes) + sep
    elif (minutes == 0):
        final_time += '00' + sep
    times = times - minutes * 60

    #handle second display
    if (times > 9):
        final_time += str(times)
    elif (times > 0):
        final_time += '0' + str(times)
    elif (times == 0):
        final_time += '00'
    return final_time

def pass_hash(password):
    """md5 hash of password in reverse order."""
    hashes = hashlib.md5(password.encode()).hexdigest()
    hashes = '-'.join(hashes).split('-')
    hashes.reverse()
    return ''.join(hashes)

def deco_file(func):
    """Decorator for file fnction for API compatibility."""
    def wrapper(name, exit_=False):
        return name
    return wrapper

@deco_file
def file(name, exit_=True):
    try:
        path = dirname(__file__)
    except NameError:
        path = ''
    path = join(path, name)
    if not isfile(path):
        if exit_: sys.exit(1) #exit(1)
        else: return ''
    return path

def connect(server, timeout=None):
    """Check if we have access to net."""
    try:
        resp = requests.urlopen(server, timeout=timeout)
    except requests.URLError:
        return
    except Exception:
        return
    if resp.code == 200:
        return True

def xml(path):
    try:
        resp = requests.urlopen(urljoin(SERVER, path)).read().decode()
    except requests.URLError:
        resp = '<error></error>'
    except Exception:
        resp = '<error></error>'
    root = ET.fromstring(resp)
    if root.tag == 'error': return
    return root

def statistics(path='/api/monitoring/traffic-statistics'):
    root = xml(path)
    if not root: return []
    stats = [['Download',
              humanize_size(root.findtext('CurrentDownload', 0)),
              humanize_size(root.findtext('TotalDownload', 0))],
             ['Upload',
              humanize_size(root.findtext('CurrentUpload', 0)),
              humanize_size(root.findtext('TotalUpload', 0))],
             ['Total',
              humanize_size(int(root.findtext('CurrentDownload', 0)) +
                            int(root.findtext('CurrentUpload', 0))),
              humanize_size(int(root.findtext('TotalDownload', 0)) +
                            int(root.findtext('TotalUpload', 0)))],
             ['Duration',
              humanize_time(root.findtext('CurrentConnectTime', 0)),
              humanize_time(root.findtext('TotalConnectTime', 0))]
             ]
    return stats

def device_info(path='/api/device/information'):
    root = xml(path)
    if not root: return []
    return [[tag.tag, tag.text] for tag in root if tag.text is not None]

def sent_received(path='/api/monitoring/traffic-statistics'):
    root = xml(path)
    if not root: return ['0 B/0 B', '00:00:00']
    data = [humanize_size(root.findtext('CurrentUpload', 0)) + '/' +
            humanize_size(root.findtext('CurrentDownload', 0)),
            humanize_time(root.findtext('CurrentConnectTime', 0))
            ]
    return data

def network(serv, ntype):
    try: ntype = int(ntype)
    except ValueError: return ''
    no_serv = 'No-Service'
    if serv == 2:
        if ntype == 0:
            return no_serv
        elif ntype in [1, 2, 3, 21, 22, 23, 27]:
            return '2G'
        elif ntype in [24, 25, 26, 28, 29, 30, 41, 42, 43,
                       44, 45, 46, 61, 62, 63, 64, 65]:
            return '3G'
        elif ntype == 101:
            return '4G'
    else:
        if ntype == 0:
            return no_serv
        elif ntype in [1, 2, 3, 13, 15]:
            return '2G'
        elif ntype in [4, 5, 6, 7, 8, 9, 10, 11, 12, 17, 18]:
            return '3G'
        elif ntype == 19:
            return '4G'
    return ''

def status(path='api/monitoring/status'):
    root = xml(path)
    if not root: return {}
    status = {'service_status':  root.findtext('ServiceStatus', 0),
              'conn_status':     root.findtext('ConnectionStatus', 900),
              'wifi_status':     root.findtext('WifiStatus', 'OFF'),
              'current_user':    root.findtext('CurrentWifiUser', 0),
              'total_user':      root.findtext('TotalWifiUser', 5),
              'signal':          root.findtext('SignalStrength', 0),
              'signal_icon':     root.findtext('SignalIcon', 0),
              'network_type':    root.findtext('CurrentNetworkType', ''),
              'network_type_ex': root.findtext('CurrentNetworkTypeEx', '')
              }
    try: serv = int(status['service_status'])
    except ValueError: pass
    ntype    = status['network_type']
    ntype_ex = status['network_type_ex']
    if serv == 2: status['network'] = network(serv, ntype_ex)
    else: status['network'] = network(serv, ntype)
    return status
