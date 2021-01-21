#!/usr/bin/env python
import time
import argparse
import httplib
import mimetypes
import json
import os
import sys
import urllib
import ssl
from base64 import b64encode

is_ssl = False
ignore_ssl_certificates = False
username = None
password = None
timeout = 120

#########################
##    Actions  python 2.7
#########################
def list_tenants(host, **kwargs):
    if host is None:
        raise Exception('Missing host')

    status, reason, resp = get_json(host, '/api/admin/tenants')
    print print_json(status, reason, resp)


def create_tenant(host, tid, **kwargs):
    company_name = kwargs.get('name')
    req = {'tenantId': tid}

    if company_name is not None:
        req['companyName'] = company_name

    status, reason, resp = post_json(host, '/api/admin/tenants', to_json(req))
    print print_json(status, reason, resp)

def create_tenant_site(host, tid, sid, name, **kwargs):
    default_locale = kwargs.get('default_locale')
    supported_locales = kwargs.get('supported_locales')
    status, reason, resp = post_json(host, '/api/admin/tenants/' + tid + '/site', to_json({
        'siteId': sid,
        'siteName': name,
        'defaultLocale': default_locale,
        'supportedLocales': [l.strip() for l in supported_locales.split(',')] if supported_locales is not None else None
    }))

    print print_json(status, reason, resp)

def delete_tenant_site(host, tid, sid, **kwargs):
    status, reason, resp = delete_json(host, '/api/admin/tenants/' + tid + '/site/' + sid)
    print print_json(status, reason, resp)

def create_cdp_db(host, tid, **kwargs):
    status, reason, resp = post_json(host, '/api/admin/tenants/' + tid + '/cdpDb', None)
    print print_json(status, reason, resp)

def migrate_to_cdp(host, tid, **kwargs):
    global timeout
    timeout = 1800
    status, reason, resp = post_json(host, '/api/admin/tenants/' + tid + '/migrateToCdp', None)
    print print_json(status, reason, resp)

def update_scoring_index(host, tid, **kwargs):
    status, reason, resp = post_json(host, '/api/admin/indexUpdate/' + tid + '/scoringIndex', None)
    print print_json(status, reason, resp)
    status, reason, resp = get_json(host, '/api/admin/indexUpdate/' + tid + '/scoringIndex', None)
    while should_watch(resp):
        time.sleep(1)
        status, reason, resp = get_json(host, '/api/admin/indexUpdate/' + tid + '/scoringIndex', None)
        print print_json(status, reason, resp)

def update_search_index(host, tid, **kwargs):
    status, reason, resp = post_json(host, '/api/admin/indexUpdate/' + tid + '/searchIndex', None)
    print print_json(status, reason, resp)
    status, reason, resp = get_json(host, '/api/admin/indexUpdate/' + tid + '/searchIndex', None)
    while should_watch(resp):
        time.sleep(1)
        status, reason, resp = get_json(host, '/api/admin/indexUpdate/' + tid + '/searchIndex', None)
        print print_json(status, reason, resp)

def update_all_indices(host, **kwargs):
    if host is None:
        raise Exception('Missing host')

    status, reason, resp = get_json(host, '/api/admin/tenants')
    tenantList = from_json(resp);
    for tenant in tenantList['tenants']:
        tid = tenant['id']
        if not tid.endswith('_draft') and tenant['active']: # ignore drafts and inactive tenants
            print '*** updating index for tenant ' + tid + ' ***'
            try:
                update_scoring_index(host, tid, **kwargs)
            except:
                print '*** failed to update scoring index for tenant ' + tid + ' ***'
            try:
                update_search_index(host, tid, **kwargs)
            except:
                print '*** failed to update search index for tenant ' + tid + ' ***'


def update_replications(host, **kwargs):
    if host is None:
        raise Exception('Missing host')

    # update replication for app databases
    status, reason, resp = put_json(host, '/api/admin/replication/', None)
    print print_json(status, reason, resp)

    status, reason, resp = get_json(host, '/api/admin/tenants')
    tenantList = from_json(resp);
    for tenant in tenantList['tenants']:
        tid = tenant['id']
        if not tid.endswith('_draft') and tenant['active']: # ignore drafts and inactive tenants
            status, reason, resp = put_json(host, '/api/admin/replication/' + tid, None)
            print print_json(status, reason, resp)


def delete_tenant(host, tid, **kwargs):
    purge = kwargs.get('purge')
    params = urllib.urlencode({'purge': purge})

    status, reason, resp = delete_json(host, '/api/admin/tenants/' + tid + '?' + params)
    print print_json(status, reason, resp)

def enable_replication(host, **kwargs):
    status, reason, resp = post_json(host, '/api/admin/replication/enable', None)
    print print_json(status, reason, resp)

def update_config(host, tid, **kwargs):
    file = kwargs.get('file')
    stdin = kwargs.get('stdin')

    if file is None and stdin is not True:
        raise Exception('Need to provide either file or stdin to update-config')

    config = sys.stdin.read() if stdin is True else open(file).read()

    yaml_flag = 'false'
    if file is not None and ('.yaml' in file or '.yml' in file):
        yaml_flag = 'true'

    draft = 'true' if kwargs.get('draft', False) else 'false'

    status, reason, resp = put_json(host, '/api/admin/tenants/' + tid + '?yaml=' + yaml_flag+'&draft='+draft, config)
    print print_json(status, reason, resp)


def update_config_property(host, tid, property, **kwargs):
    file = kwargs.get('file')
    stdin = kwargs.get('stdin')

    if file is None and stdin is not True:
        raise Exception('Need to provide either file or stdin to update-config')

    config = sys.stdin.read() if stdin is True else open(file).read()

    draft = 'true' if kwargs.get('draft', False) else 'false'

    status, reason, resp = put_json(host, '/api/admin/tenants/' + tid + '/' + property + '?draft='+draft + ('&siteId='+kwargs.get('sid', None) if kwargs.get('sid', None) is not None else ''), config)
    print print_json(status, reason, resp)




def get_config(host, tid, **kwargs):
    show_defaults = 'true' if kwargs.get('show_defaults', False) else 'false'
    is_yaml = kwargs.get('yaml', False)
    yaml = 'true' if is_yaml else 'false'
    status, reason, resp = get_json(host, '/api/admin/tenants/' + tid + ('.yaml' if is_yaml else '.json') + '?showDefaults='+show_defaults)
    if is_yaml:
        print print_yaml(status, reason, resp)
    else:
        print print_json(status, reason, resp)

def get_config_property(host, tid, property, **kwargs):
    draft = 'true' if kwargs.get('draft', False) else 'false'
    status, reason, resp = get_json(host, '/api/admin/tenants/' + tid + '/' + property + '?draft='+draft + ('&siteId='+kwargs.get('sid', None) if kwargs.get('sid', None) is not None else ''))
    print print_json(status, reason, resp)




def update_jobs(host, tid, **kwargs):
    csvFile = kwargs.get('csv')
    jsonFile = kwargs.get('json')
    zipFile = kwargs.get('zip')
    stdin = kwargs.get('stdin')
    watch = kwargs.get('watch', False)
    incremental = kwargs.get('incremental', False)
    remap = kwargs.get('remap', 'false')

    if remap.lower() == 'false':
        remap = False;
    else:
        remap = True;

    if csvFile is None and zipFile is None and jsonFile is None and stdin is not True:
        raise Exception('Need to provide either csv, zip, json, or stdin based csv')

    file_name = None
    file_contents = None
    input_type = None
    if csvFile is not None:
        file_name = os.path.basename(csvFile)
        file_contents = open(csvFile).read()
        input_type = 'jobsCsv'
    elif jsonFile is not None:
        file_name = os.path.basename(jsonFile)
        file_contents = open(jsonFile).read()
        input_type = 'jobsJson'
    elif zipFile is not None:
        file_name = os.path.basename(zipFile)
        file_contents = open(zipFile, 'rb').read()
        input_type = 'jobsZip'
    elif stdin is True:
        file_name = 'stdin.csv'
        file_contents = sys.stdin.read()
        input_type = 'jobsCsv'

    status, reason, resp = post_multipart(host, '/api/admin/jobUpdates', [('tenantId', tid),
                                                                          ('base64Encoded', 'false'),
                                                                          ('incremental',
                                                                           'true' if incremental else 'false'),
                                                                          ('remap', 'true' if remap else 'false')], [(
        input_type,
        file_name,
        file_contents
    )])
    print print_json(status, reason, resp)

    if watch:
        task_id = get_task_id_from_res(resp)
        while should_watch(resp):
            time.sleep(1)
            status, reason, resp = get_json(host, '/api/admin/jobUpdates/' + tid + '/' + (
                task_id if task_id is not None else 'last'))
            print print_json(status, reason, resp)


def get_update_jobs_status(host, tid, **kwargs):
    watch = kwargs.get('watch', False)
    task_id = kwargs.get('id')

    status, reason, resp = get_json(host,
                                    '/api/admin/jobUpdates/' + tid + '/' + (task_id if task_id is not None else 'last'))
    print print_json(status, reason, resp)

    if watch:
        while should_watch(resp):
            time.sleep(1)
            status, reason, resp = get_json(host,
                                            '/api/admin/jobUpdates/' + tid + '/' + task_id if task_id is not None else 'last')
            print print_json(status, reason, resp)


def get_all_job_statusses(host, **kwargs):
    duration = kwargs.get('duration', None)
    status, reason, resp = get_json(host, '/api/admin/jobUpdates', to_json({
        'duration': duration
    }))
    print print_json(status, reason, resp)


def update_industry_categorization_indexes(host, **kwargs):
    tid = kwargs.get('tid')
    url = '/api/admin/jobUpdates/industryCategorization'
    if tid is not None:
        url += '/' + tid
    status, reason, resp = post_json(host, url, None)
    print print_json(status, reason, resp)

def get_industry_categorization_index_state(host, **kwargs):
    status, reason, resp = get_json(host, '/api/admin/jobUpdates/industryCategorization', None)
    print print_json(status, reason, resp)


def remap_jobs(host, **kwargs):
    csvFile = kwargs.get('csv')
    stdin = kwargs.get('stdin')
    tid = kwargs.get('tid')
    mapping_function = kwargs.get('mapping_function')
    html_fields = kwargs.get('html_fields')
    limit = kwargs.get('limit')

    if csvFile is None and stdin is not True:
        raise Exception('Need to provide either csv, or stdin based csv')

    file_name = None
    file_contents = None
    if csvFile is not None:
        file_name = 'jobs.csv'
        file_contents = open(csvFile).read()
    elif stdin is True:
        file_name = 'jobs.csv'
        file_contents = sys.stdin.read()

    args = []
    if tid is not None:
        args.append(('tid', tid))
    if html_fields is not None:
        args.append(('htmlFields', html_fields))
    if limit is not None:
        args.append(('limit', limit))
    if mapping_function is not None:
        if os.path.isfile(mapping_function):
            args.append(('mappingFunction', open(mapping_function).read()))
        else:
            args.append(('mappingFunction', mapping_function))

    status, reason, resp = post_multipart(host, '/api/admin/jobUpdates/remap', args, [(
        'jobsCsv',
        file_name,
        file_contents
    )])

    print print_json(status, reason, resp)


def update_job_cat_skills(host, tid, **kwargs):
    watch = kwargs.get('watch', False)
    status, reason, resp = post_json(host, '/api/admin/jobUpdates/' + tid + '/updateJobCategorySkills', None)
    print print_json(status, reason, resp)

    if watch:
        task_id = get_task_id_from_res(resp)
        while should_watch(resp):
            time.sleep(1)
            status, reason, resp = get_json(host, '/api/admin/jobUpdates/' + tid + '/' + (
                task_id if task_id is not None else 'last'))
            print print_json(status, reason, resp)

def get_tenant_jobs(host, tid, **kwargs):
    if host is None or tid is None:
        raise Exception('Missing host or tid')

    status, reason, resp = get_json(host, '/api/admin/jobsExport/' + tid)
    print print_json(status, reason, resp)


def funnel_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'plain':
        mime = 'text/plain'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    elif kwargs.get('format') == 'html':
        mime = 'text/html'
    elif kwargs.get('format') == 'excel':
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('before') is not None:
        args['before'] = kwargs.get('before')
    if kwargs.get('after') is not None:
        args['after'] = kwargs.get('after')
    if kwargs.get('time_period') is not None:
        args['timePeriod'] = kwargs.get('time_period')

    status, reason, resp = get_by_mime(host, '/api/admin/reports/' + tid + '/funnel', mime, args)

    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'wb' if kwargs.get('format') == 'excel' else 'w')
        f.write(resp)
        f.close()
    else:
        print resp


def usage_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'plain':
        mime = 'text/plain'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    elif kwargs.get('format') == 'html':
        mime = 'text/html'
    elif kwargs.get('format') == 'excel':
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('before') is not None:
        args['before'] = kwargs.get('before')
    if kwargs.get('after') is not None:
        args['after'] = kwargs.get('after')
    if kwargs.get('time_period') is not None:
        args['timePeriod'] = kwargs.get('time_period')
    if kwargs.get('include_daily') is not None:
        args['includeDaily'] = 'true' if kwargs.get('include_daily') else 'false'
    if kwargs.get('hide_sections') is not None:
        args['hideSections'] = kwargs.get('hide_sections')

    status, reason, resp = get_by_mime(host, '/api/admin/reports/' + tid + '/usage', mime, args)


    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'wb' if kwargs.get('format') == 'excel' else 'w')
        f.write(resp)
        f.close()
    else:
        print resp


def intent_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'plain':
        mime = 'text/plain'
    elif kwargs.get('format') == 'csv':
        mime = 'text/csv'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    elif kwargs.get('format') == 'html':
        mime = 'text/html'
    elif kwargs.get('format') == 'excel':
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('before') is not None:
        args['before'] = kwargs.get('before')
    if kwargs.get('after') is not None:
        args['after'] = kwargs.get('after')
    if kwargs.get('time_period') is not None:
        args['timePeriod'] = kwargs.get('time_period')

    url = '/api/admin/reports/' + tid + '/intents'
    if kwargs.get('intent') is not None:
        url += '/' + kwargs.get('intent')

    status, reason, resp = get_by_mime(host, url, mime, args)


    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'wb' if kwargs.get('format') == 'excel' else 'w')
        f.write(resp)
        f.close()
    else:
        print resp


def keyword_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'plain':
        mime = 'text/plain'
    elif kwargs.get('format') == 'csv':
        mime = 'text/csv'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    elif kwargs.get('format') == 'html':
        mime = 'text/html'
    elif kwargs.get('format') == 'excel':
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('before') is not None:
        args['before'] = kwargs.get('before')
    if kwargs.get('after') is not None:
        args['after'] = kwargs.get('after')
    if kwargs.get('time_period') is not None:
        args['timePeriod'] = kwargs.get('time_period')

    status, reason, resp = get_by_mime(host, '/api/admin/reports/' + tid + '/keywords', mime, args)

    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'wb' if kwargs.get('format') == 'excel' else 'w')
        f.write(resp)
        f.close()
    else:
        print resp


def intent_list_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'csv':
        mime = 'text/csv'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('locale') is not None:
        args['locale'] = kwargs.get('locale')

    status, reason, resp = get_by_mime(host, '/api/admin/reports/' + tid + '/intent-list', mime, args)

    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'w')
        f.write(resp)
        f.close()
    else:
        print resp


def content_pane_list_report(host, tid, **kwargs):
    mime = None
    if kwargs.get('format') is None or kwargs.get('format') == 'plain':
        mime = 'text/plain'
    elif kwargs.get('format') == 'json':
        mime = 'application/json'
    elif kwargs.get('format') == 'html':
        mime = 'text/html'
    elif kwargs.get('format') == 'csv':
        mime = 'text/csv'
    else:
        raise Exception('invalid format type')

    args = {}
    if kwargs.get('locale') is not None:
        args['locale'] = kwargs.get('locale')

    status, reason, resp = get_by_mime(host, '/api/admin/reports/' + tid + '/content-pane-list', mime, args)


    if kwargs.get('format') == 'json':
        resp = print_json(status, reason, resp)

    if kwargs.get('output') is not None:
        f = open(kwargs.get('output'), 'w')
        f.write(resp)
        f.close()
    else:
        print resp


#########################
##    Utilities
#########################

def get_conn(host):
    global is_ssl
    global ignore_ssl_certificates
    global timeout

    if is_ssl:
        if ignore_ssl_certificates:
            return httplib.HTTPSConnection(host, timeout=timeout, context=ssl._create_unverified_context())
        else:
            return httplib.HTTPSConnection(host, timeout=timeout)
    else:
        return httplib.HTTPConnection(host, timeout=timeout)


def to_json(js):
    return json.dumps(js)


def from_json(js):
    return json.loads(js)


def print_json(status, reason, js):
    if status >= 200 and status < 300:
        try:
            return json.dumps(from_json(js), sort_keys=True, indent=2, separators=(',', ': '))
        except:
            print 'Error code: ', status
            print 'Reason: ', reason
            print 'Response: ', js
            raise ValueError, 'Couldn\'t parse json response: ' + js
    else:
        print 'Error code: ', status
        print 'Reason: ', reason
        raise ValueError, 'Server server returned error code %s' % status

def print_yaml(status, reason, yaml):
    if status >= 200 and status < 300:
        return yaml
    else:
        print 'Error code: ', status
        print 'Reason: ', reason
        raise ValueError, 'Server server returned error code %s' % status


def should_watch(res):
    if res is None:
        return False

    js = from_json(res)

    if 'state' not in js:
        return False

    if js['state'] is None or js['state'] == 'UPDATED' or js['state'] == 'FAILED':
        return False

    return True


def get_task_id_from_res(res):
    if res is None:
        return None

    js = from_json(res)
    if '_id' not in js:
        return None
    return js['_id']


def join_dict(a, b):
    res = a.copy()
    res.update(b)
    return res


def authenticate():
    global username
    global password
    if username is not None and password is not None:
        # user_and_pass = b64encode(b"scm:password").decode("ascii")
        user_and_pass = b64encode(b"" + username + b":" + password).decode("ascii")
        return {'Authorization': 'Basic %s' % user_and_pass}
    else:
        return {}


def get_json(host, url, body=None, headers=None):
    headers = join_dict(authenticate(), headers or {})
    conn = get_conn(host)
    conn.request('GET', url, body=body, headers=join_dict(headers, {'Content-Type': 'application/json'}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def get_by_mime(host, url, mime, params, headers=None):
    headers = join_dict(authenticate(), headers or {})
    conn = get_conn(host)
    conn.request('GET', url + '?' + urllib.urlencode(params), headers=join_dict(headers, {'Accept': mime}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def put_json(host, url, body, headers=None):
    headers = join_dict(authenticate(), headers or {})
    conn = get_conn(host)
    conn.request('PUT', url, body=body, headers=join_dict(headers, {'Content-Type': 'application/json'}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def delete_json(host, url, headers=None):
    headers = join_dict(authenticate(), headers or {})
    conn = get_conn(host)
    conn.request('DELETE', url, headers=join_dict(headers, {'Content-Type': 'application/json'}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def post_json(host, url, body, headers=None):
    headers = join_dict(authenticate(), headers or {})
    conn = get_conn(host)
    conn.request('POST', url, body=body, headers=join_dict(headers, {'Content-Type': 'application/json'}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def post_multipart(host, uri, fields, files, headers=None):
    headers = join_dict(authenticate(), headers or {})
    content_type, body = encode_multipart_formdata(fields, files)
    conn = get_conn(host)
    conn.request('POST', uri, body, headers=join_dict(headers, {'Content-Type': content_type}))
    resp = conn.getresponse()
    return resp.status, resp.reason, resp.read()


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------bound@ry_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def main():
    global is_ssl
    global ignore_ssl_certificates
    global username
    global password

    defaults_file = os.path.expanduser('~/at-admin.json')
    defaults = None
    if os.path.isfile(defaults_file):
        print 'Loading defaults: ' + defaults_file
        defaults = json.loads(open(defaults_file).read())
    else:
        print 'Defaults not found: ' + defaults_file

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='at-admin.py', description='Attractive admin server rest client')
    parser.add_argument('--host', help='server host', required=defaults is None or not 'host' in defaults)
    parser.add_argument('-u', '--username', help='basic auth username',
                        required=defaults is None or not 'username' in defaults)
    parser.add_argument('-p', '--password', help='basic auth password',
                        required=defaults is None or not 'password' in defaults)
    parser.add_argument('--ssl', help='This is an ssl connection, if not inferred from url path', action='store_true')
    parser.add_argument('--ignore-ssl-certificates', help='Ignore strict ssl certificate verification',
                        action='store_true')
    subparsers = parser.add_subparsers(title='sub-commands', help='Sub-command meaning')

    # create the parser for the "list-tenants" command
    parser_list_tenants = subparsers.add_parser('list-tenants', help='List all tenants on the server')
    parser_list_tenants.set_defaults(cmd=list_tenants)

    # create the parser for the "create-tenant" command
    parser_create_tenant = subparsers.add_parser('create-tenant', help='Create a new tenant')
    parser_create_tenant.set_defaults(cmd=create_tenant)
    parser_create_tenant.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_create_tenant.add_argument('-n', '--name', help='The name of the tenant to create')
    # parser_create_tenant.add_argument('bar', type=int, help='bar help')

    # create the parser for the "create-cdp-db" command
    parser_create_cdp_db = subparsers.add_parser('create-cdp-db', help='Create CDP database for an existing tenant')
    parser_create_cdp_db.set_defaults(cmd=create_cdp_db)
    parser_create_cdp_db.add_argument('-t', '--tid', help='The id of the tenant', required=True)

    # create the parser for the "migrate-to-cdp" command
    parser_migrate_to_cdp = subparsers.add_parser('migrate-to-cdp', help='Migrate the job data of an existing tenant to CDP database')
    parser_migrate_to_cdp.set_defaults(cmd=migrate_to_cdp)
    parser_migrate_to_cdp.add_argument('-t', '--tid', help='The id of the tenant', required=True)

    # create the parser for the "update_scoring_index" command
    parser_update_scoring_index = subparsers.add_parser('update-scoring-index', help='Update scoring index for an existing tenant')
    parser_update_scoring_index.set_defaults(cmd=update_scoring_index)
    parser_update_scoring_index.add_argument('-t', '--tid', help='The id of the tenant', required=True)

    # create the parser for the "update_search_index" command
    parser_update_scoring_index = subparsers.add_parser('update-search-index', help='Update search index for an existing tenant')
    parser_update_scoring_index.set_defaults(cmd=update_search_index)
    parser_update_scoring_index.add_argument('-t', '--tid', help='The id of the tenant', required=True)

    # create the parser for the "update-all-indices" command
    parser_update_all_indices = subparsers.add_parser('update-all-indices', help='Update scoring index and search index for all tenants')
    parser_update_all_indices.set_defaults(cmd=update_all_indices)

    # create the parser for the "enable-replication" command
    parser_enable_replication = subparsers.add_parser('enable-replication', help='Enable replication to config Database')
    parser_enable_replication.set_defaults(cmd=enable_replication)

    # create the parser for the "update-replications" command
    parser_update_replications = subparsers.add_parser('update-replications', help='Update replications for all attractive Cloudant databases')
    parser_update_replications.set_defaults(cmd=update_replications)

    # create the parser for the "delete-tenant" command
    parser_delete_tenant = subparsers.add_parser('delete-tenant',
                                                 help='Either deactivates or purges a tenant')
    parser_delete_tenant.set_defaults(cmd=delete_tenant)
    parser_delete_tenant.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_delete_tenant.add_argument('--purge', action='store_true', default=False,
                                      help='Drop all of a tenant\'s tables.  Irreversible and permanent.' +
                                           'The tenant can not be recreated with the same id.')

    parser_create_tenant_site = subparsers.add_parser('create-site',
                                                     help='Creates a new site for a tenant')
    parser_create_tenant_site.set_defaults(cmd=create_tenant_site)
    parser_create_tenant_site.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_create_tenant_site.add_argument('-s', '--sid', help='The id of the site to create', required=True)
    parser_create_tenant_site.add_argument('-n', '--name', help='The display name of the site in the admin ui', required=True)
    parser_create_tenant_site.add_argument('-l', '--default-locale', help='The default locale of the site', required=False)
    parser_create_tenant_site.add_argument('--supported-locales', help='The comma separated list of locales this site supports')

    parser_delete_tenant_site = subparsers.add_parser('delete-site',
                                                      help='Creates a new site for a tenant')
    parser_delete_tenant_site.set_defaults(cmd=delete_tenant_site)
    parser_delete_tenant_site.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_delete_tenant_site.add_argument('-s', '--sid', help='The id of the site to create', required=True)


    # create the parser for the "update-config" command
    parser_update_config = subparsers.add_parser('update-config',
                                                 help='Updates a tenant\'s client config')
    parser_update_config.set_defaults(cmd=update_config)
    parser_update_config.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_update_config.add_argument('-f', '--file', help='The path to the json config file')
    parser_update_config.add_argument('--draft', action='store_true', default=False,
                                      help='Store this change in draft mode only (default is to update both draft and prod)')
    parser_update_config.add_argument('-x', '--stdin', action='store_true',
                                      help='Read config file from stdin (for pipe redirection)')

    # create a parser to update a config property
    parser_update_config_property = subparsers.add_parser('update-config-property',
                                                          help='Updates a single property in a client\'s config')
    parser_update_config_property.set_defaults(cmd=update_config_property)
    parser_update_config_property.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_update_config_property.add_argument('-s', '--sid', help='The  site id', required=False)
    parser_update_config_property.add_argument('-p', '--property', help='The config property to update', required=True)
    parser_update_config_property.add_argument('--draft', action='store_true', default=False,
                                               help='Store this change in draft mode only (default is to update both draft and prod)')
    parser_update_config_property.add_argument('-f', '--file', help='The path to the json config file')
    parser_update_config_property.add_argument('-x', '--stdin', action='store_true',
                                               help='Read config file from stdin (for pipe redirection)')


    # create the parser for the "get-config" command
    parser_get_config = subparsers.add_parser('get-config',
                                              help='Gets a tenant\'s client config')
    parser_get_config.set_defaults(cmd=get_config)
    parser_get_config.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_get_config.add_argument('--show-defaults', action='store_true', default=False,
                                              help='Include the default values in the config file')
    parser_get_config.add_argument('--yaml', action='store_true', default=False,
                                   help='Get this config file in yaml format')

    parser_get_config_property = subparsers.add_parser('get-config-property',
                                          help='Gets a tenant\'s client config')
    parser_get_config_property.set_defaults(cmd=get_config_property)
    parser_get_config_property.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_get_config_property.add_argument('-s', '--sid', default=None,
                                            help='Get the get the config for this site id')
    parser_get_config_property.add_argument('--draft', action='store_true', default=False,
                                            help='Get the draft mode version of the config (as seen in the admin ui)')
    parser_get_config_property.add_argument('-p', '--property', help='The config property to update', required=True)



    # create the parser for the "update-jobs" command
    parser_update_jobs = subparsers.add_parser('update-jobs',
                                               help='Update a tenant\'s jobs')
    parser_update_jobs.set_defaults(cmd=update_jobs)
    parser_update_jobs.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_update_jobs.add_argument('-c', '-f', '--csv', '--file',
                                    help='The path to a csv file containing the tenant\'s jobs')
    parser_update_jobs.add_argument('-j', '--json',
                                    help='The path to a json file containing the tenant\'s already annotated jobs')
    parser_update_jobs.add_argument('-z', '--zip',
                                    help='The path to a zip file, containing a csv file, containing the tenant\'s jobs')
    parser_update_jobs.add_argument('-x', '--stdin', action='store_true',
                                    help='Read csv containing the tenant\'s jobs from stdin')
    parser_update_jobs.add_argument('-i', '--incremental', action='store_true',
                                    help='This csv contains only the differences from the current jobs, not the whole jobs list')
    parser_update_jobs.add_argument('-r', '--remap',
                                    help='Set to not remap the CSV columns according to the config mappingFunction when creating JSON jobs in the database')
    parser_update_jobs.add_argument('-w', '--watch', action='store_true', default=False,
                                    help='Watch changes to the job update status until completion')

    # create the parser for the "update-jobs-status" command
    parser_get_update_jobs_status = subparsers.add_parser('get-update-jobs-status',
                                                          help='Get the status from an update jobs task')
    parser_get_update_jobs_status.set_defaults(cmd=get_update_jobs_status)
    parser_get_update_jobs_status.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_get_update_jobs_status.add_argument('--id', help='The id of the job update task to get')
    parser_get_update_jobs_status.add_argument('-w', '--watch', action='store_true', default=False,
                                               help='Watch changes to the job update status until completion')

    # create the parser for getting all job statusses
    parser_get_update_all_jobs_status = subparsers.add_parser('get-all-update-jobs-status',
                                                          help='Get the job update status across all tenants')
    parser_get_update_all_jobs_status.set_defaults(cmd=get_all_job_statusses)
    parser_get_update_all_jobs_status.add_argument('-d', '--duration', help='how long to go back for', required=False)

    # create the parser for forcing all tenants to update their industry categorization indexes
    parser_update_industry_categorization = subparsers.add_parser('update-industry-categorization-index-versions',
                                                              help='Update the industry category indexes for all tenants using the latest model')
    parser_update_industry_categorization.add_argument('-t', '--tid', help='The id of the tenant', required=False)
    parser_update_industry_categorization.set_defaults(cmd=update_industry_categorization_indexes)


    # create parser to get what indexes are deployed for each tenant
    parser_get_industry_categorization = subparsers.add_parser('get-industry-categorization-index-versions',
                                                                  help='Lookup what industry categorization models are indexed for each tenant')
    parser_get_industry_categorization.set_defaults(cmd=get_industry_categorization_index_state)


    # create the parser for remapping jobs
    parser_remap_jobs = subparsers.add_parser('remap-jobs',
                                              help='Test remapping a client\'s jobs')
    parser_remap_jobs.set_defaults(cmd=remap_jobs)
    parser_remap_jobs.add_argument('-t', '--tid',
                                   help='Auto load the mapping function of this tenant (either provide this or the mapping function and html fields)')
    parser_remap_jobs.add_argument('-m', '--mapping-function', help='The mapping function')
    parser_remap_jobs.add_argument('--html-fields', help='Which fields should be parsed as html')
    parser_remap_jobs.add_argument('-l', '--limit', help='How many records to return before stopping')
    parser_remap_jobs.add_argument('-x', '--stdin', action='store_true',
                                   help='Read csv containing the tenant\'s jobs from stdin')
    parser_remap_jobs.add_argument('-c', '-f', '--csv', '--file',
                                   help='The path to a csv file containing the tenant\'s jobs', required=True)

    # create the parser for the "update-job-cat-skills" command
    parser_update_job_cat_skills = subparsers.add_parser('update-job-cat-skills',
                                                         help='Update a tenant\'s job category skills using the tenants current jobs')
    parser_update_job_cat_skills.set_defaults(cmd=update_job_cat_skills)
    parser_update_job_cat_skills.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_update_job_cat_skills.add_argument('-w', '--watch', action='store_true', default=False,
                                              help='Watch changes to the job update status until completion')
    # create the parser for the "get-tenant-jobs" command
    parser_get_tenant_jobs = subparsers.add_parser('get-tenant-jobs', help='get a json dump of the jobs for a tenant')
    parser_get_tenant_jobs.add_argument('-t', '--tid', help='The id of the tenant', required=True)
    parser_get_tenant_jobs.set_defaults(cmd=get_tenant_jobs)

    parser_funnel_report = subparsers.add_parser('funnel-report', help='Get an funnel report for a tenant')
    parser_funnel_report.set_defaults(cmd=funnel_report)
    parser_funnel_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_funnel_report.add_argument('-b', '--before', help='When the reports should before')
    parser_funnel_report.add_argument('-a', '--after', help='When the reports should after')
    parser_funnel_report.add_argument('-p', '--time-period',
                                      help='The duration of the report (if only providing before or after)')
    parser_funnel_report.add_argument('-f', '--format',
                                      help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_funnel_report.add_argument('-o', '--output', help='Where to output the results to (defaults to stdout)')

    parser_usage_report = subparsers.add_parser('usage-report', help='Get an usage report for a tenant')
    parser_usage_report.set_defaults(cmd=usage_report)
    parser_usage_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_usage_report.add_argument('-b', '--before', help='When the reports should before')
    parser_usage_report.add_argument('-a', '--after', help='When the reports should after')
    parser_usage_report.add_argument('-p', '--time-period',
                                     help='The duration of the report (if only providing before or after)')
    parser_usage_report.add_argument('-f', '--format',
                                     help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_usage_report.add_argument('-o', '--output', help='Where to output the results to (defaults to stdout)')
    parser_usage_report.add_argument('-d', '--include-daily', help='Include a daily breakdown in the report',
                                     action='store_true', default=False)
    parser_usage_report.add_argument('-hide', '--hide-sections', help='Hide sections to this report like (userActivity,jobSearch,feedback)')

    parser_intent_report = subparsers.add_parser('intent-report', help='Get an intent report for a tenant')
    parser_intent_report.set_defaults(cmd=intent_report)
    parser_intent_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_intent_report.add_argument('-b', '--before', help='When the reports should before')
    parser_intent_report.add_argument('-a', '--after', help='When the reports should after')
    parser_intent_report.add_argument('-p', '--time-period',
                                      help='The duration of the report (if only providing before or after)')
    parser_intent_report.add_argument('-i', '--intent', help='Get the report for this single intent')
    parser_intent_report.add_argument('-f', '--format',
                                      help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_intent_report.add_argument('-o', '--output', help='Where to output the results to (defaults to stdout)')

    parser_keyword_report = subparsers.add_parser('keyword-report', help='Get an keyword report for a tenant')
    parser_keyword_report.set_defaults(cmd=keyword_report)
    parser_keyword_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_keyword_report.add_argument('-b', '--before', help='When the reports should before')
    parser_keyword_report.add_argument('-a', '--after', help='When the reports should after')
    parser_keyword_report.add_argument('-p', '--time-period',
                                       help='The duration of the report (if only providing before or after)')
    parser_keyword_report.add_argument('-f', '--format',
                                       help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_keyword_report.add_argument('-o', '--output', help='Where to output the results to (defaults to stdout)')

    parser_intent_list_report = subparsers.add_parser('intent-list-report', help='List all of the intents for a tenant')
    parser_intent_list_report.set_defaults(cmd=intent_list_report)
    parser_intent_list_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_intent_list_report.add_argument('-l', '--locale',
                                           help='What locale do you want to get the intents for (default is English)')
    parser_intent_list_report.add_argument('-f', '--format',
                                           help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_intent_list_report.add_argument('-o', '--output', help='Where to output the results to (defaults to stdout)')

    parser_content_pane_list_report = subparsers.add_parser('content-pane-list-report',
                                                            help='List all of the content panes for a tenant')
    parser_content_pane_list_report.set_defaults(cmd=content_pane_list_report)
    parser_content_pane_list_report.add_argument('-t', '--tid', help='The tenant to get the reports for', required=True)
    parser_content_pane_list_report.add_argument('-l', '--locale',
                                                 help='What locale do you want to get the intents for (default is English)')
    parser_content_pane_list_report.add_argument('-f', '--format',
                                                 help='The format of the report, plain, html, or json are valid values (json is default)')
    parser_content_pane_list_report.add_argument('-o', '--output',
                                                 help='Where to output the results to (defaults to stdout)')

    args = parser.parse_args()
    args_dict = None
    if defaults is not None:
        defaults.update(
            dict((k, v) for k, v in vars(args).iteritems() if v))  # magic inside update is to remove null values
        args_dict = defaults
        del args_dict['cmd']
    else:
        args_dict = vars(args)

    # httplib.HTTPConnection(host) doesn't want http prefix it wants the hostname/port
    if 'http://' in args_dict['host']:
        args_dict['host'] = args_dict['host'].replace('http://', '')
        is_ssl = False

    if 'https://' in args_dict['host']:
        args_dict['host'] = args_dict['host'].replace('https://', '')
        is_ssl = True

    if args_dict.get('ssl') is not None and args_dict.get('ssl') is not False:
        is_ssl = True

    if args_dict.get('username') is not None:
        username = args_dict.get('username')

    if args_dict.get('password') is not None:
        password = args_dict.get('password')

    if args_dict.get('ignore_ssl_certificates') is not None:
        ignore_ssl_certificates = True

    args.cmd(**args_dict)


if __name__ == '__main__':
    main()
