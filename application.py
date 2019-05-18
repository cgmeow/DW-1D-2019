# importing relevant modules
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import more_itertools
import matplotlib.pyplot as plt
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.switch import Switch
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import firebase_admin
from firebase_admin import credentials, firestore

# linking to firebase
cred = credentials.Certificate(r"api.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# setting up of Login Screen
class LoginScr(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = FloatLayout()

        # Displaying User and Password for using to input 
        self.passw_inp = TextInput(height=60, hint_text='password', pos_hint={'x': .2, 'y': 0.3}, size_hint=(0.6, 0.1),
                                   multiline=False, password=True)
        self.un_inp = TextInput(height=60, hint_text='username', pos_hint={'x': .2, 'y': 0.425}, size_hint=(0.6, 0.1),
                                multiline=False)
        confirm = Button(text='Log in', pos_hint={'x': .2, 'y': .15}, size_hint=(0.6, 0.1))
        quitbutton = Button(text="Quit", font_size=15, pos_hint={'x': 0.9, 'y': 0.9}, size_hint=(0.1, 0.1),
                            background_normal='', background_color=(1, 0, 0, 1))
        fake_forgot = Label(text='forgot password?', pos_hint={'x': .3, 'y': .07}, size_hint=(0.4, 0.1))
        logo = Image(source='logo.jpg', pos_hint={'x': 0.1, 'y': .5}, size_hint=(0.8, 0.5))

        # bind the keys to make it functional
        confirm.bind(on_press=self.validate_user)
        quitbutton.bind(on_press=self.quit_app)

        # add widget 
        self.layout.add_widget(self.un_inp)
        self.layout.add_widget(self.passw_inp)
        self.layout.add_widget(confirm)
        self.layout.add_widget(quitbutton)
        self.layout.add_widget(fake_forgot)
        self.layout.add_widget(logo)
        self.add_widget(self.layout)

    # if username and password match, screen changes to 'Home'
    # otherwise clear user input
    def validate_user(self, something):
        usr_inp = self.un_inp.text
        psw_inp = self.passw_inp.text
        try:
            # data = u'{}'.format(usr_inp)

            user = db.collection(u'Users').document(usr_inp)
            user = user.get().to_dict()
            password = user['Password']  # admin
            if psw_inp == password:
                self.manager.transition.direction = 'left'
                App.get_running_app().actual_name = user['Name']

                # modify the current screen to "Home"
                self.manager.current = 'Home'
            else:
                self.un_inp.text = ''
                self.passw_inp.text = ''
        except:
            self.un_inp.text = ''
            self.passw_inp.text = ''

    # transition to Home Screen
    def change_to_home(self, value):
        self.manager.transition.direction = 'right'
        self.manager.current = 'Home'

    # quit app
    def quit_app(self, value):
        App.get_running_app().stop()


# setting up of Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation='vertical')
        menubar = GridLayout(cols=3, rows=1, size_hint_y=None, spacing=5)
        content = GridLayout(cols=2, size_hint=(1, 1), spacing=0.2)
        # Core menu layouts
        home_button = Label(text='Home', font_size=24, size_hint_x=.3)
        anal_button = Button(text='Analytics', on_press=self.change_to_analytics, font_size=24, size_hint_x=.3)
        log_button = Button(text='Log', on_press=self.change_to_log, font_size=24, size_hint_x=.3)
        quit_button = Button(text="X", font_size=24, pos_hint={'x': 0.9, 'y': 0.9}, size_hint=(0.1, 0.1),
                             background_normal='', background_color=(1, 0, 0, 1))

        menubar.add_widget(home_button)
        menubar.add_widget(anal_button)
        menubar.add_widget(log_button)

        # creating welcome label
        accy = App.get_running_app().actual_name
        welcome_label = Label(text="Welcome back, {}! ".format(accy), font_name='Lobster-Regular', size_hint=(1, None),
                              font_size=60)

        # setting up of bluetooth, intrusion, universal unlocking and sms setup, linking them to firebase
        # instantiate widgets
        bluetooth_label1 = Label(text="Registered Devices :", font_size=24, halign='right', )
        bluetooth_label2 = Label(text=" {}".format(self.bluetooth_display()), font_size=24)

        intrusion_label = Label(text="Last Intrusion:", font_size=24, halign='right')
        intrusion_status = Label(text="{}".format(self.check_intrusion()), font_size=24, halign='right')

        uni_unlock_label = Label(text="Lock :", font_size=24, halign='right')
        switch_button = Switch(active=self.check_status()[0])

        sms_setup = Label(text="Alert mode status :", font_size=24, halign='right')
        sms_switch = Switch(active=self.check_status()[1])

        # add widgets
        content.add_widget(bluetooth_label1)
        content.add_widget(bluetooth_label2)
        content.add_widget(intrusion_label)
        content.add_widget(intrusion_status)
        content.add_widget(uni_unlock_label)
        content.add_widget(switch_button)
        content.add_widget(sms_setup)
        content.add_widget(sms_switch)

        # bind buttons to functions
        anal_button.bind(on_press=self.change_to_analytics)
        log_button.bind(on_press=self.change_to_log)
        quit_button.bind(on_press=self.quit_app)
        switch_button.bind(active=self.uni_unlock)
        sms_switch.bind(active=self.change_notif)

        # add widgets
        self.layout.add_widget(welcome_label)
        self.layout.add_widget(content)
        self.layout.add_widget(menubar)

        # quit app
        self.add_widget(quit_button)
        self.add_widget(self.layout)

    # screen transition to analytics
    def change_to_analytics(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'Analytics'

    # screen transition to log
    def change_to_log(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'Log'

    def quit_app(self, value):
        App.get_running_app().stop()

    # checking for intrusion, logging intrusions
    def check_intrusion(self):
        db = firestore.client()
        timeref = db.collection(u'Users').document(u'Admin').collection(u'Timestamps').document(
            u'Timestamps').get().to_dict()
        intrusionlogs = timeref['Intrusions']
        return intrusionlogs[-1]

    # displaying bluetooth ID
    def bluetooth_display(self):
        db = firestore.client()
        admin_ref = db.collection(u'Users').document(u'Admin')

        admin = admin_ref.get()
        admin_dict = admin.to_dict()
        display_bluetooth = admin_dict['BluetoothID']

        return display_bluetooth[0]

    # check door status via firebase
    def check_status(self):
        admin_ref = db.collection(u'Users').document(u'Admin').get().to_dict()
        status_lock = admin_ref['LockStatus']
        status_notif = admin_ref['Notification']

        return status_lock, status_notif

    # method creating the slider to unlock door from anywhere in the world
    def uni_unlock(self, instance, value):
        admin_ref = db.collection(u'Users').document(u'Admin')

        if value == True:
            admin_ref.update({u'RemoteLock': 'Lock'})

        elif value == False:
            admin_ref.update({u'RemoteLock': 'Unlock'})

    # updating firebase regarding notification status
    def change_notif(self, instance, value):
        admin_ref = db.collection(u'Users').document(u'Admin')
        if value == True:
            admin_ref.update({u'Notification': True})

        elif value == False:
            admin_ref.update({u'Notification': False})


# creating multiple lists to store data
enter_ls = []
enter_date_ls = []
enter_time_ls = []
leave_ls = []
leave_date_ls = []
leave_time_ls = []

# initialise figure and set background of analytics page
fig = plt.figure()
fig.patch.set_facecolor('black')

# setting the colours of the axes
with plt.rc_context({'axes.edgecolor': 'white', 'xtick.color': 'white', 'ytick.color': 'white'}):
    # get data from db for timelogs (enter, leave, intrusion)
    stamper = db.collection(u'Users').document(u'Admin').collection(u'Timestamps').document(
        u'Timestamps').get().to_dict()
    # get enter timestamp in list
    enter_time = stamper['Enter']
    # get leave timestamp in list
    leave_time = stamper['Leave']

    for i in enter_time:
        # split at space into enter date and time
        enter_ls.append(i.split(' '))

    enter_ls = list(more_itertools.flatten(enter_ls))  # flatten list

    for a in enter_ls:
        if enter_ls.index(a) % 2 == 0:
            enter_date_ls.append(a)  # enter date in list
        elif enter_ls.index(a) % 2 != 0:
            enter_time_ls.append(a)  # enter time in list

    for j in leave_time:
        # split at space into leave date and time
        leave_ls.append(j.split(' '))

    leave_ls = list(more_itertools.flatten(leave_ls))  # flatten list

    for b in leave_ls:
        if leave_ls.index(b) % 2 == 0:
            leave_date_ls.append(b)  # leave date in list
        elif leave_ls.index(b) % 2 != 0:
            leave_time_ls.append(b)  # leave time in list

    # storing data obtain in list form
    time_in_sec_enter_ls = []
    for i in enter_time_ls:
        t = sum(x * int(i) for x, i in zip([3600, 60, 1], i.split(":")))
        time_in_sec_enter_ls.append(t)

    # storing data obtain in list form
    time_in_sec_leave_ls = []
    for i in leave_time_ls:
        t = sum(x * int(i) for x, i in zip([3600, 60, 1], i.split(":")))
        time_in_sec_leave_ls.append(t)

    # setting the range of the graph, and colour coding data, displaying it in histogram form
    bin_edge = range(0, 86400, 1800)
    plt.hist(time_in_sec_leave_ls, bins=bin_edge, color=['red'])
    plt.hist(time_in_sec_enter_ls, bins=bin_edge, color=['blue'])

    # label that was showed in original graph
    label = [0, 20000, 40000, 60000, 80000]
    new_label = ['00:00:00', '05:33:20', '11:06:40', '16:40:00', '22:13:20']
    # change from seconds to hh:mm:ss
    plt.xticks(label, new_label)

    # change the inside of the graph
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('salmon')

    # plotting the actual graph
    legend = ['Leave', 'Enter']
    plt.legend(legend)
    plt.xlabel('Time', color='white')
    plt.ylabel('Frequency', color='white')
    plt.title('Cumulative Activity In A Week', color='white')


# Sets up the Analytics Screen
class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation='vertical')

        menubar = GridLayout(cols=3, rows=1, size_hint_y=None, spacing=5)
        home_button = Button(text='Home', on_press=self.change_to_home, font_size=24, size_hint_x=.3)
        anal_button = Label(text='Analytics', font_size=24, size_hint_x=.3)
        log_button = Button(text='Log', on_press=self.change_to_log, font_size=24, size_hint_x=.3)

        # binding functions to the 3 buttons upon pushing
        home_button.bind(on_press=self.change_to_home)
        log_button.bind(on_press=self.change_to_log)

        # adding widget to the 3 buttons to make it functional
        menubar.add_widget(home_button)
        menubar.add_widget(anal_button)
        menubar.add_widget(log_button)

        # Retrieves data to plot
        data = FigureCanvasKivyAgg(plt.gcf())

        # add anchor layouts to box layouts
        self.layout.add_widget(data)
        self.layout.add_widget(menubar)
        self.add_widget(self.layout)

    # transitions to the Home Screen
    def change_to_home(self, value):
        self.manager.transition.direction = 'right'
        self.manager.current = 'Home'

    # transitions to the Log Screen
    def change_to_log(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'Log'


# Sets up the Log screen
class LogScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation='vertical')
        menubar = GridLayout(cols=3, rows=1, size_hint_y=None, spacing=5)
        home_button = Button(text='Home', on_press=self.change_to_home, font_size=24, size_hint_x=.3)
        anal_button = Button(text='Analytics', on_press=self.change_to_analytics, font_size=24, size_hint_x=.3)
        log_button = Label(text='Log', font_size=24, size_hint_x=.3)

        # bind buttons to functions
        home_button.bind(on_press=self.change_to_home)
        anal_button.bind(on_press=self.change_to_analytics)

        # adds widgets for the 3 buttons at the bottom of the Log screen
        menubar.add_widget(home_button)
        menubar.add_widget(anal_button)
        menubar.add_widget(log_button)

        # add anchor layouts to box layouts
        self.layout.add_widget(self.tabler())
        self.layout.add_widget(menubar)
        self.add_widget(self.layout)

    # create table to display log
    def tabler(self):
        result = BoxLayout(size_hint_y=0.9, orientation='vertical')
        title = GridLayout(cols=3, rows=1, size_hint_y=0.1)
        layout = GridLayout(cols=3, size_hint_y=None, spacing=5)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))

        # instantiate table elements
        headings1 = Label(text='Index', halign='center', size_hint_x=None)
        headings2 = Label(text='Enter')
        headings3 = Label(text='Leave')
        title.add_widget(headings1)
        title.add_widget(headings2)
        title.add_widget(headings3)
        listings = self.firebase_retrieval()
        entry = listings[0][::-1]
        leave = listings[1][::-1]

        # append the new entries from database to new rows in table
        for i in range(len(leave)):
            index = Label(text=str(i + 1), height=40, halign='center', size_hint_x=None)
            btn_entry = Button(text=entry[i], size_hint_y=None, height=40, width=100)
            btn_leave = Button(text=leave[i], size_hint_y=None, height=40, width=100)
            layout.add_widget(index)
            layout.add_widget(btn_entry)
            layout.add_widget(btn_leave)

        # adding widget for the scroller
        result.add_widget(title)
        scroller = ScrollView(size_hint=(1, 0.9))
        scroller.add_widget(layout)
        result.add_widget(scroller)
        return result

    # retrieves the data stored on firebase for kivy to display
    def firebase_retrieval(self):
        db = firestore.client()
        timelogs = db.collection(u'Users').document(u'Admin').collection(u'Timestamps').document(u'Timestamps')
        timelog_entry = timelogs.get().to_dict()['Enter']
        timelog_leave = timelogs.get().to_dict()['Leave']
        return timelog_entry, timelog_leave

    # screen transition to the home screen
    def change_to_home(self, value):
        self.manager.transition.direction = 'right'
        self.manager.current = 'Home'

    # screen transition to the data analytics screen
    def change_to_analytics(self, value):
        self.manager.transition.direction = 'right'
        self.manager.current = 'Analytics'


# creating the screen transitions between the Login, Analytics, Logs and Home screens
class SwitchScreenApp(App):
    actual_name = 'Johnny'

    def build(self):
        s_m = ScreenManager()
        lg_s = LoginScr(name='Login')
        h_s = HomeScreen(name='Home')
        l_s = LogScreen(name='Log')
        a_s = AnalyticsScreen(name='Analytics')
        # adding widgets to all the screens
        s_m.add_widget(lg_s)
        s_m.add_widget(h_s)
        s_m.add_widget(l_s)
        s_m.add_widget(a_s)
        s_m.current = 'Login'

        return s_m


# initialise the app
if __name__ == '__main__':
    SwitchScreenApp().run()
