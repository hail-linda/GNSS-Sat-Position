# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  $filename :     Transform between GNSS time and UTC                                                            +
#                                                                              +
#            Copyright (c) 2021.  by Y.Xie, All rights reserved.               +
#                                                                              +
#   references :                                                               +
#       [1] GPX The GNSS Time transformation https://www.gps.gov/technical/icwg/
#                                                                              +
#   version : $Revision:$ $Date:$                                              +
#   history : 2020/12/11  1.0  new                                             +
#             26/01/2021, 16:57  1.1  modify                               +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def utctoweekseconds(utc, leapseconds):
    """ Returns the GPS week, the GPS day, and the seconds
        and microseconds since the beginning of the GPS week """
    import datetime, calendar
    utc = datetime.datetime.strptime(utc, "%Y-%m-%dT%H:%M:%S")
    datetimeformat = "%Y-%m-%dT%H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06T00:00:00", datetimeformat)
    # tdiff = utc - epoch + datetime.timedelta(seconds=leapseconds)
    tdiff = utc - epoch + datetime.timedelta(seconds=leapseconds)
    gpsweek = tdiff.days // 7
    gpsdays = tdiff.days - 7 * gpsweek
    gpsseconds = tdiff.seconds + 86400 * (tdiff.days - 7 * gpsweek)
    return gpsweek, gpsseconds, gpsdays


def weeksecondstoutc(gpsweek, gpsseconds, leapseconds):
    import datetime, calendar
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00", datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek * 7), seconds=(gpsseconds - leapseconds))
    utc_time = datetime.datetime.strftime(epoch + elapsed, datetimeformat)
    print('UTC time of the time-reading')
    print('>>', utc_time)
    print('>>', calendar.day_name[(epoch + elapsed).weekday()])