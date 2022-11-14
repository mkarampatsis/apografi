#!/usr/bin/env python3
import sys
from datetime import datetime
from time import mktime
sys.path.append("/home/oper/utils")
from mongoutils import profiles, passwords, changes, syncdata
import logging
import argparse

date = datetime.now()

depdict = {
    '1': 201,
    '2': 209,
    '3': 217,
    '4': 231,
    '5': 235,
    '6': 225,
    '7': 241,
    '8': 229,
    '9': 246,
}

logging.basicConfig(
    filename="changes_from_registars.log",
    format="%(asctime)s %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.DEBUG)


def get_profile_doc(username):
    profdoc = profiles.find_one({'username': username})
    passdoc = passwords.find_one({"username": username})

    student = None
    if profdoc['category']['id'] == '1':
        userdata = profdoc['studdata']['userdata']
        registrations = profdoc['studdata']['registrations']

        birthdate = userdata['birthdate']
        birthYear = birthdate.split('/')[2] if len(birthdate) > 1 else ''

        student = {
            'registrationID': userdata['studentid'],
            'departmentID': depdict[profdoc['department']['id']],
            'birthYear': birthYear,
            'enrollmentType': 'Undergraduate',
            'enrollmentTerm': registrations[-1]['semester']
            if registrations else '',
            'attendanceType': '',
            'enrollmentStatus': 'active',
            'inscriptionAcYear': repr(int(userdata['yearOfEntry']) - 1)
            if userdata['yearOfEntry'] else '',
            'inscriptionTerm': userdata['semesterOfEntry'],
            'inscriptionMethodID': '',
            'inscriptionNumber': userdata['panelliniesID'],
        }

    if passdoc:
        password = {
            'password-hash': passdoc['posix'],
            'nt-hash': passdoc['samba']['nthash']
        }
    else:
        password = None

    datefmt = '%Y-%m-%d'
    try:
        tmpvaliduntil = profdoc['status']['validuntil']
        validuntil = mktime(
            datetime.strptime(tmpvaliduntil, datefmt).timetuple())
    except:
        validuntil = ""

    if validuntil:
        timestamps = {'validuntil': validuntil}
    else:
        timestamps = None

    externalemail = profdoc['emails']['external']['email']
    forwardemail = profdoc['emails']['forward']['email']
    if 'ntuapersonmail' in profdoc['emails']:
        ntuapersonmailemail = profdoc['emails']['ntuapersonmail']['email']
    else:
        ntuapersonmailemail = ''

    emails = {
        'mail': externalemail,
        'ntuapersonmail': ntuapersonmailemail,
        'forwardmail': forwardemail,
    }

    try:
        staffid = profdoc['paycode']
    except:
        staffid = None

    entry = {
        'active': not profdoc['status']['disabled'],
        'username': profdoc['username'],
        'password': password,
        'sn': profdoc['lastname'],
        'givenname': profdoc['firstname'],
        'department': profdoc['department'],
        'category': profdoc['category']
    }

    if password:
        entry['password'] = password
    if timestamps:
        entry['timestamps'] = timestamps
    if emails:
        entry['emails'] = emails
    if student:
        entry['student'] = student
    if staffid:
        entry['staffID'] = staffid
    return entry


def get_nocsync_doc(username):
    syncdoc = syncdata.find_one({'username': username})
    return syncdoc


def find_required_sync_doc_changes(profdoc, syncdoc):
    # returns a list of fields that require change
    ulist = []
    if 'student' in profdoc and not 'timestamps' in profdoc:
        if profdoc['student'] != syncdoc['student']:
            #print("1>>>",profdoc['student'])
            #print("2>>>",syncdoc['student'])
            ulist.append('student')

    if profdoc['password'] != syncdoc['password']:
        ulist.append('password')

    if 'timestamps' in profdoc:
        if profdoc['timestamps']['validuntil'] != syncdoc['timestamps'][
                'validuntil']:
            print("3>>", profdoc['timestamps']['validuntil'])
            ulist.append('validuntil')

    if profdoc['emails']['mail'] != syncdoc['emails']['mail']:
        ulist.append('externalemail')
    if profdoc['emails']['ntuapersonmail'] != syncdoc['emails'][
            'ntuapersonmail']:
        ulist.append('ntuapersonmail')
    if profdoc['emails']['forwardmail'] != syncdoc['emails']['forwardmail']:
        ulist.append('forwardmail')

    if 'staffID' in profdoc:
        if profdoc['staffID'] != syncdoc['staffID']:
            ulist.append('staffID')

    if profdoc['active'] != syncdoc['active']:
        ulist.append('active')
    if profdoc['sn'] != syncdoc['sn']:
        ulist.append('sn')
    if profdoc['givenname'] != syncdoc['givenname']:
        #print ("1>>", profdoc['givenname'])
        #print ("2>>", syncdoc['givenname'])
        ulist.append('givenname')
    if profdoc['category']['id'] != '1':
        if profdoc['department'] != syncdoc['department']:
            #print("1>>>", profdoc['department'])
            #print("2>>>", syncdoc['department'])
            ulist.append('department')
        if profdoc['category'] != syncdoc['category']:
            #print("1>>>",profdoc['category'])
            #print("2>>>",syncdoc['category'])
            ulist.append('category')

    if 'staffID' in profdoc:
        if 'ids' in profdoc:
            if profdoc['ids'] != syncdoc['ids']:
                ulist.append('ids')
        else:
            ulist.append('ids')

    return ulist


def update_changes(username, fields):

    if 'ids' in fields:
        change = {
            "username": username,
            "type": "agent",
            "change": {
                "reset": "NocSync Data",
                "fields": fields
            },
            "date": date,
            "synced": {
                "mongo": False
            }
        }
    else:
        change = {
            "username": username,
            "type": "agent",
            "change": {
                "reset": "NocSync Data",
                "fields": fields
            },
            "date": date,
            "synced": {
                "mongo": True,
                "nocsync": False
            }
        }

    changes.insert_one(change)
    return change


def create_change_from_updated_data(username, dry_run=True):
    # most updates originate from registars, others from Kostas' updates on nocsync
    # profile collection is already updated from registars (createProfilePX crontab)
    sync_doc = get_nocsync_doc(username)
    if sync_doc:
        prof_doc = get_profile_doc(username)

        fields = find_required_sync_doc_changes(prof_doc, sync_doc)

        if len(fields) > 0:
            if dry_run:
                print("[Dry Run] Will create new change for {} ({})".format(
                    username, fields))
                return username
            else:
                update_changes(username, fields)
                logging.info(
                    "Created new change for {} ({})".format(username, fields))


def batch_iterator():
    for document in profiles.find({
            'category.id': {
                '$in': ['1']
            },
            'status.disabled': False,
            'department.id': '9',
            'studdata.userdata.yearOfEntry': 2021
    }):
        yield document


def batch_dry_run():
    print("Batch Dry Run")
    ulist = []
    for document in batch_iterator():
        username = document["username"]
        ulist.append(create_change_from_updated_data(username))
    alist = [x for x in ulist if x is not None]
    print("{} documents will be affected".format(len(alist)))


def batch_run():
    for document in batch_iterator():
        username = document["username"]
        create_change_from_updated_data(username, False)


my_parser = argparse.ArgumentParser(
    prog="changes_from_registars.py",
    usage="%(prog)s [--dryrun] username|batch",
    description="Creates changes(s) from registar data if run in batch else from profile and nocsync")

my_parser.add_argument("-dryrun", "--dryrun", action="store_true")
my_parser.add_argument("what", type=str, help="username|batch")
args = my_parser.parse_args()

if args.dryrun:
    if args.what == "batch":
        batch_dry_run()
    else:
        create_change_from_updated_data(args.what)
else:
    if args.what == "batch":
        batch_run()
        #pass
    else:
        create_change_from_updated_data(args.what, False)