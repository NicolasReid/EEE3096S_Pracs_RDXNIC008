import datetime
#import time
#rtc = time.clock_gettime(time.CLOCK_REALTIME)

#while(time.clock_gettime(time.CLOCK_REALTIME)-rtc < 5):
#    pass

#print("System RTC", time.clock_gettime(time.CLOCK_REALTIME))
print("+==========+==========+")
now = datetime.datetime.now()
for i in range(10):
    print("Timestamp: ", now.timestamp())
    print (now.strftime("%H:%M:%S"))
