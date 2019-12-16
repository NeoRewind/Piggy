from teacher import PiggyParent
import sys
import time

class Piggy(PiggyParent):

    '''
    *************
    SYSTEM SETUP
    *************
    '''

    def __init__(self, addr=8, detect=True):
        PiggyParent.__init__(self) # run the parent constructor

        ''' 
        MAGIC NUMBERS <-- where we hard-code our settings
        '''
        self.LEFT_DEFAULT = 78
        self.RIGHT_DEFAULT = 80
        self.MIDPOINT = 1500  # what servo command (1000-2000) is straight forward for your bot?
        self.corner_count = 0
        self.load_defaults()
        self.SAFE_Distance = 250
        self.start_direction = 0
        self.start_time = 0
        
        

    def load_defaults(self):
        """Implements the magic numbers defined in constructor"""
        self.set_motor_limits(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_limits(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.set_servo(self.SERVO_1, self.MIDPOINT)
        
          
    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values. Python is cool.
        # Please feel free to change the menu and add options.
        print("\n *** MENU ***") 
        menu = {"n": ("Navigate", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "h": ("Hold position", self.hold_position),
                "c": ("Calibrate", self.calibrate),
                "q": ("Quit", self.quit),
                "v": ("Veer", self.slither)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = str.lower(input("Your selection: "))
        # activate the item selected
        menu.get(ans, [None, self.quit])[1]()

    '''
    ****************
    STUDENT PROJECTS
    ****************
    '''

    def dance(self):
        """Begin Dancing I Hope It Works""" 
        # check to see it's safe
        if not self.safe_to_dance():
            print ("Not Going to Dance")
            return # return closes doen the method
        else:
            print("It's Safe to Dance")
        for x in range(3):
         self.stopgoback()
         self.spin()
         self.stopgo()
         self.shake()
    
    def safe_to_dance(self):
        """Does a 360 distance chack and returns true if safe"""
        for x in range(4):
            for angle in range(1000, 2001, 100):
                self.servo(angle)
                time.sleep(.1)
                if self.read_distance() < 250:
                    return False
            self.turn_by_deg(90)
        return True

         
        
    def scan(self):
        """Sweep the servo and populate the scan_data dictionary"""
        for angle in range(self.MIDPOINT-350, self.MIDPOINT+350,300):
            self.servo(angle)
            self.scan_data[angle] = self.read_distance()

    def obstacle_count(self):
        """Does a 360 scan and returns the number of obsatcles it sees"""
        found_something = False #trigger
        trigger_distance = 250
        count = 0
        starting_position = self.get_heading() #write down starting position
        self.right(primary=60, counter=-60)
        time.sleep(.2)
        while abs(self.get_heading() - starting_position) < 2:
            if self.read_distance() < trigger_distance and not found_something:
                found_something = True
                count += 1
                print ("/n FOUND SOMETHING /n")
            elif self.read_distance() > trigger_distance and found_something:
                found_something = False
                print("I have a clear view. Resetting my counter")
        self.stop()
        print("I have found this many things: %d" % count)
        return count
         
    def quick_check(self):
        #Three checks
        for ang in range(self.MIDPOINT-300,self.MIDPOINT+301,300):
            self.servo(ang)
            if self.read_distance() < self.SAFE_Distance:
                return False
        #Have servo scan while moving
        return True
    
    def slither(self):
        """practice a smooth veer"""
        starting_direction = self.get_heading() #write down start

        # drive forward
        self.set_motor_power(self.MOTOR_LEFT, self.LEFT_DEFAULT)
        self.set_motor_power(self.MOTOR_RIGHT, self.RIGHT_DEFAULT)
        self.fwd()

        # throttle down left motor 
        for power in range(self.LEFT_DEFAULT, 30, -10):
            self.set_motor_power(self.MOTOR_LEFT, power)
            time.sleep(.5)

            
        #throttle up left 
        for power in range(30, self.LEFT_DEFAULT + 1, 10):
            self.set_motor_power(self.MOTOR_LEFT, power)
            time.sleep(.1)
        
        #throttle down the right
        for power in range(self.RIGHT_DEFAULT, 30, -10):
            self.set_motor_power(self.MOTOR_RIGHT, power)
            time.sleep(.5)

        # throttle up right
        for power in range(30, self.RIGHT_DEFAULT + 1, 10):
            self.set_motor_power(self.MOTOR_RIGHT, power)
            time.sleep(.1)

        left_speed = self.LEFT_DEFAULT
        right_speed = self.RIGHT_DEFAULT

        #straighten out
        while self.get_heading() != starting_direction:
            if self.get_heading() < starting_direction:
                right_speed -= 10
        elif self.get_heading() > starting_direction:
                left_speed -=10
        self.set_motor_power(self.MOTOR_LEFT, left_speed)
        self.set_motor_power(self.MOTOR_RIGHT, right_speed)
        time.sleep(.1)
        
       

    def nav(self):
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("I will begin to navigate the maze. I hope I can leave")
        self.corner_count = 0 #attempt to fix corner issue

        self.start_direction = self.get_heading() #record beginning direction ... Need to fix
        while True: 
            while self.quick_check(): # When the distance is more tham # ...
                self.corner_count = 0
                self.fwd() #TO DO: Begin to anticipate problems Ahead 
                time.sleep(.01) #Move and check distance every .01 seconds
            self.stop()
            # self.check_distance() # turn using check_dist
            if not self.exit_path():
                self.average_distance() # turn using average_dist
    
    def exit_path(self):
        where_I_was = self.get_heading()
        self.turn_to_deg(self.start_direction)
        if self.quick_check():
            return True
        else:
            self.turn_to_deg(where_I_was)
            

    def average_distance(self): #Check distance
        self.scan()
        self.corner_count += 1
        if self.corner_count > 4:
            self.get_out_of_corner()
            return
        #traversal
        left_total = 0
        left_count = 0
        right_total = 0
        right_count = 0
        for ang, dist in self.scan_data.items(): #Set _total and _count values
            if ang < self.MIDPOINT:
                right_total += dist
                right_count += 1
            else:
                left_total += dist
                left_count += 1

        left_avg = left_total / left_count
        right_avg = right_total / right_count
        if left_avg > right_avg: #Move by 45 deg wherever average is less
            self.turn_by_deg(-45)
        else:
            self.turn_by_deg(45)

    def get_out_of_corner(self): # Method to escape corner
        self.turn_by_deg(180)
        self.deg_fwd(720)

    def maze_time(self): #This Method will keep track of time spent in maze
        #when thge robot is picked up, tell time and shut off
        pass
      
    def hold_position(self):
        started_at = self.get_heading()
        while True:
            time.sleep(.1)
            current_angle = self.get_heading()
            if abs(started_at - current_angle) > 20:
                self.turn_to_deg(started_at)
            

    def check_distance(self): # Additional distance method
        self.servo(1000)
        time.sleep(.01)
        l = self.read_distance()
        self.servo(2000)
        time.sleep(.01)
        r = self.read_distance()
        if l > r:
            self.turn_by_deg(-45)
        elif r > l:
            self.turn_by_deg(45)


    def shake(self):
        """Do a cool spin and turn servo"""
        #Need to Fix Servo
        self.right(primary=90, counter=0)
        self.servo(2000)
        time.sleep(1)
        self.servo(1000)
        time.sleep(1)
        self.servo(2000)
        time.sleep(1)
        self.servo(1000)
        time.sleep(1)
        self.servo(2000)
        time.sleep(.1)
        self.stop()
        time.sleep(.1)
        self.left(primary=90, counter=0)
        self.servo(2000)
        time.sleep(1)
        self.servo(1000)
        time.sleep(1)
        self.servo(2000)
        time.sleep(1)
        self.servo(1000)
        time.sleep(1)
        self.servo(2000)
        time.sleep(.1)
        self.stop()
        time.sleep(.25)
            

    def spin(self):
        """Spin 180 and move forward"""
        self.turn_by_deg(180)
        time.sleep(.25)
        self.stop
        time.sleep(.25)
        self.fwd()
        time.sleep(.5)
        self.stop
        time.sleep(.25)
        self.turn_by_deg(180)
        time.sleep(.25)
        self.stop
        time.sleep(.25)
        self.fwd()
        time.sleep(.5)
        self.stop
        time.sleep(.25)
        self.turn_by_deg(180)


        
    def stopgo(self):
        #Fix wheel stength
        """Stop and go"""
        self.fwd()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.fwd()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.fwd()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.fwd()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.fwd()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.fwd()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)

    def stopgoback(self):
        """stop and go backwards w/spin"""
        self.back()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.back()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.back()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.turn_by_deg(180)
        time.sleep(.25)
        self.back()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.back()
        self.servo(1000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.back()
        self.servo(2000)
        time.sleep(.25)
        self.stop()
        time.sleep(.5)
        self.turn_by_deg(180)
        time.sleep(.25)




###########
## MAIN APP
if __name__ == "__main__":  # only run this loop if this is the main file

    p = Piggy()

    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x\n")
        p.quit()

    try:
        while True:  # app loop
            p.menu()

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        p.quit()  
