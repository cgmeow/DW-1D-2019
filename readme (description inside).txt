----- What can this app do? -----

This software + hardware suit is able to detect any intrusions at your dorm room. It then (according to your preferences)
notifies you by sms of any of such intrusions. The app also allows you to open your dorm room from ANYWHERE in the world.
With bluetooth enabled, you no longer need a keycard for your dorm room, as the room will auto unlock and lock when you
approach and leave the room respectively.

For analysis, we included your weekly time spent in the room. This is done easily by gathering the timelogs available. We
also included a feature in the app where you are able to see how many checkins and checkouts were made, to truly understand
your social life in SUTD

Enjoy!


----- Part 1: Installing Dependencies -----

1) Store all the files in the 'Application' folder into a file directory of your choice
2) Open this file directory using your preferred Python IDE (PyCharm & virtual environment recommended)
3) Open terminal and proceed with the following command: 'pip3 install -r req.txt'. This will install all modules/libraries
    required for this application. *Manually install these packages if the installation fails
4) Now, run the following command in terminal : 'garden install graph'
4) Launch the App

----- Part 2: Understanding the application -----

1) To test out the app, enter the following credentials (Character sensitive)
    - Username : 'Admin'
    - Pass: admin
     (If there are any issues, please contact sheikhsalim@mymail.sutd.edu.sg)

2) The App consists of 3 tabs, as follows:
    - Home : Offers information, buttons to control 'remote open' and enable sms-notifications if intrusion detected
    - Analytics : Provides a glimpse of the user's activity (amount of time spent in the room) throughout the week
    - Logs : Provides a timelog for all entrances/leaves since the beginning of time
    ** tabs are available at the bottom of the screen for easy access


----- Part 3: Towards the RPI -----


1) Attached is also the code for the RPi. To launch, make sure to have the following modules pip-ed on the RPi:
    - pip3 install libdw
    - pip3 install Rpi.GPIO
    - pip3 install twilio

2) Run the following on the RPi's terminal:
    - 'sudo apt-get update'
    - 'sudo apt-get install python-pip python-dev ipython'
    - 'sudo apt-get install bluetooth libbluetooth-dev'
    - 'sudo pip install pybluez'

3) Store the folder 'RPi' into a file directory of your choice. Launch the application. Voila!


Done by: Cheryl Lui, Ng Jia Yi, Ng Ming Bing, Tay Kiat Hong, Sheikh Salim  from F06