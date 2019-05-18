import bluetooth
import RPi.GPIO as GPIO
import time
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client


# Firebase Authentications
cred = credentials.Certificate("api.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
admin_ref = db.collection(u'Users').document(u'Admin')


# Get the bluetooth IDs and phone number for authenticated users from Firebase
user_data = admin_ref.get().to_dict()
bt_add = user_data['BluetoothID']
user_phone = user_data['PhoneNumber']


#Checks the user's security preference
sms_mode = user_data['Notification']

# Twilio Necessities (for SMS messaging)
account_sid = 'ACe9dd23baafde6d279b831632ade4ede9'
auth_token = '4c8183e3b5a28cfbb9c043d3bfbe60ae'
client = Client(account_sid, auth_token)
myTwilioNumber = '+12052932808'  # This number is for Twilio's service


# These are for declaring the GPIO servo motor and sensor (IR)
servoPIN = 18
sensorPIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(sensorPIN, GPIO.IN)
pwm = GPIO.PWM(servoPIN, 50)
pwm.start(0)

# The following are angle values for the servo that correspond to
# locking and unlocking door (respectively)
lock_door = 145
unlock_door = 55


# The function 'SetAngle' takes in a particular angle value and proceeds to
# actuate the servo motor with the value of angle provided
def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(servoPIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servoPIN, False)
    pwm.ChangeDutyCycle(0)


# The function 'motion_detected' checks if there are any positive
# sensor readigns by the IR. A positive reading suggests that there
# is motion detected, hence returning true
def motion_detected():
    if GPIO.input(sensorPIN) == 1:  # value of 1 indicates PIR detected motion
        print("motion detected")
        return True


# The fucntion 'send_sms' takes in a string argument and proceeds
# to send a message containing that string.


def send_sms(text):
    message = client.messages \
        .create(
            body=text,  # content of text
            from_=myTwilioNumber,  # Twilio sending number
            to=user_phone  # Receiving number
        )
    print(message.sid)  # Prints out confirmation ID via console


# The 'uni_remote' function takes in two arguments, firebase_inst and
# session_status (described later). The function queries firebase for the
# 'RemoteLock' field and executes the user's request. This alllows
# locking and unlocking of door from anywhere in the world

def uni_remote(firebase_inst, in_session):
    admin_dict = firebase_inst.get().to_dict()
    if admin_dict['RemoteLock'] == 'Lock':  # if user request lock
        SetAngle(lock_door)
        # Updates firebase statuses
        firebase_inst.update({u'RemoteLock': 'None'})
        firebase_inst.update({u'LockStatus': True})
        return False
    elif admin_dict['RemoteLock'] == 'Unlock':  # if user request unlock
        SetAngle(unlock_door)
        # Updates firebase statuses
        firebase_inst.update({u'RemoteLock': 'None'})
        firebase_inst.update({u'LockStatus': False})
        return True

    return in_session


# This function serves to check if an authenticated bluetooth nearby_devices
# is disconnected. It also runs additional measures to ensure that phantom
# disconnects are not counted
def bluetooth_disconnect():
    total_disconnection = 0
    for i in range(3):  # scans for 3 intervals
        nearby_devices = bluetooth.discover_devices(
                    lookup_names=False, duration=1)  # each interval 1s scan
        if not any(x in nearby_devices for x in bt_add):  # if bt not detected
            total_disconnection += 1
        else:
            total_disconnection = 0
    if total_disconnection < 3:  # if phantom disconnects exist
        return False
    else:
        return True


# This function serves to automatically lock and unlock the door as the
# user leaves the range of the door
def bluetooth_remote(firebase_inst, in_session):
    # check to see if universal remote is in session, proceed to skip if true
    if in_session:
        return None

    nearby_devices = bluetooth.discover_devices(lookup_names=False, duration=2)
    lockstatus = firebase_inst.get().to_dict()['LockStatus']
    # Obtaining timelogs to be appended to
    timelogs = firebase_inst.collection(
        u'Timestamps').document(u'Timestamps')
    # Seperating timelogs for entry and leaving
    timelog_entry = timelogs.get().to_dict()['Enter']
    timelog_leave = timelogs.get().to_dict()['Leave']
    print('timelog for entry', timelog_entry)

    # If bluetooth device is nearby and door is locked, unlock the door
    # and proceed to update timelog for 'enter' on firebase
    if any(x in nearby_devices for x in bt_add) and lockstatus is True:
        SetAngle(unlock_door)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timelog_entry.append(current_time)
        firebase_inst.update({u'LockStatus': False})
        timelogs.update({u'Enter': timelog_entry})

    # If bluetooth device is moving away and door is unlocked, lock the door
    # and procced to update timelog for 'leave' on firebase
    elif bluetooth_disconnect() and lockstatus is False:
        SetAngle(lock_door)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timelog_leave.append(current_time)
        firebase_inst.update({u'LockStatus': True})
        timelogs.update({u'Leave': timelog_leave})

# This function is for Intrusion Detection. Alerts user accoridingly
# with respect to security preferences (specified in app)
def intrusion_detection(firebase_inst, in_session, sms_mode):
    # check to see if universal remote is in session, proceed to skip if true
    if in_session:
        return False
    timelogs = firebase_inst.collection(u'Timestamps').document(u'Timestamps')
    timelog_intrusion = timelogs.get().to_dict()['Intrusions']

    if bluetooth_disconnect() and motion_detected():
        # Logs the instance of intrusion
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timelog_intrusion.append(current_time)
        timelogs.update({u'Intrusions': timelog_intrusion})
        if sms_mode:
            send_sms("Intrusion is suspected to be currently ongoing")
            time.sleep(10)
        return True

    return False


# toggler_session is crucial for our remote lock/unlock function.
# It makes sure that bluetooth auto lock is disabled during a remote session
# Remote unlocks are treated as seperate sessions and will not be logged
toggler_session = False
# intrusion_status reflects the suspected intrusion
intrusion_status = False
# sets initial status of door upon first boot to 'locked'
SetAngle(lock_door)
admin_ref.update({u'LockStatus': True})
while True:
    # Scans firebase for each iteration of the loops for crucial changes
    db = firestore.client()
    firebase_instance = db.collection(u'Users').document(u'Admin')
    # Calls upon 3 functions per loop
    toggler_session = uni_remote(firebase_instance, toggler_session)
    intrusion_status = intrusion_detection(firebase_instance, toggler_session,
                                           sms_mode)
    bluetooth_remote(firebase_instance, toggler_session)
