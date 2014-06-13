#!/usr/bin/env python
import datetime
import time
import csv

def convert_to_seconds(time):
    """Converts the give time to total seconds since midnight"""
    total_seconds = time.hour*60*60
    total_seconds += time.minute*60
    total_seconds += time.second
    return(total_seconds)

class time_range_class:
    """A class for carrying around time ranges such as 8:00-12:00"""
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = self.calculate_total_time()
    
    def __repr__(self):
        return_string = "{} to {}".format(self.start_time, self.end_time)
        return(return_string)
    
    def calculate_total_time(self):
        """Returns the total time in hours"""
        seconds_difference = convert_to_seconds(self.end_time) - convert_to_seconds(self.start_time)
        hours_difference = float(seconds_difference)/60/60
        return(hours_difference)

class working_day_class:
    """A class containing a single day's working information"""
    def __init__(self, date, times):
        self.date = date
        self.times = times
        self.total_time = self.calculate_total_time()
    
    def __repr__(self):
        return_string = "{}: {}".format(self.date, self.total_time)
        return(return_string)
    
    def calculate_total_time(self):
        """Rturns the total time for the day in hours"""
        total_time = 0.0
        for time_range in self.times:
            total_time += time_range.total_time
        self.total_time = total_time
        return(total_time)

def strip_time(time_string):
    """Strips out a datetime.time object for the string formatted as %H:%M:%S"""
    the_time = datetime.datetime.strptime(time_string, "%H:%M:%S")
    the_time = the_time.time()
    return(the_time)

def strip_date(date_string):
    """Strips out a datetime.date object for the string formatted as %m-%d-%Y %H:%M:%S"""
    the_date = datetime.datetime.strptime(date_string, "%m/%d/%Y %H:%M")
    the_date = the_date.date()
    return(the_date)

def import_working_time_csv_data(filename):
    """Imports working time data for a signle person from a properly  formatted.csv file.
        HACK assumes a very specific format for the csv file"""
    
    file = open(filename)
    data_reader = csv.reader(file, delimiter=',')
    exception_times = []
    default_days = {'1':[], '2':[], '3':[], '4':[], '5':[], '6':[], '7':[], }
    is_default_day = False
    
    for row in data_reader:
        
        if row[0] == "Default Days":
            is_default_day = True
        
        elif row[0] == "END Default Days":
            is_default_day = False
        
        elif is_default_day == True:
            if row[1] == '' or row[1] == '0':
                row[1] = '0:00:00'
            if row[2] == '' or row[2] == '0':
                row[2] = '0:00:00'
            start_time = strip_time(row[1])
            end_time = strip_time(row[2])
            time_range = time_range_class(start_time, end_time)
            default_days[row[0]].append(time_range)
        
        elif is_default_day == False:
            the_date = strip_date(row[0])
            if row[2] == '' or row[2] == '0':
                row[2] = '0:00:00'
            if row[3] == '' or row[3] == '0':
                row[3] = '0:00:00'
            start_time = strip_time(row[2])
            end_time = strip_time(row[3])
            time_range = time_range_class(start_time, end_time)
            #if exception_times != []:
                #print(the_date, exception_times[-1].date)
            if exception_times != [] and the_date == exception_times[-1].date: ##HACK assumes ordered properly
                exception_times[-1].times.append(time_range)
                exception_times[-1].calculate_total_time()
            else:
                working_day = working_day_class(the_date, [time_range])
                exception_times.append(working_day)
    
    return(default_days, exception_times)

def find_weekday(a_date):
    """Finds the integer weekday of the given date where Sunday is 1 and Saturday is 7"""
    isoweekday = a_date.isoweekday()
    if isoweekday == 7:
        isoweekday = 1
    else:
        isoweekday += 1
    return(isoweekday)

class resource_calendar_class:
    """Class for resouce calendar storing and comprenhension"""
    def __init__(self, resource_name, project_start_date, project_end_date, default_days, exception_times):
        self.project_start_date = project_start_date
        self.project_end_date = project_end_date
        self.resource_name = resource_name
        self.default_days = default_days
        self.exception_times = exception_times
        self.data = self.create_data()
    
    def create_data(self):
        """Uses the default_days and exception_times to create a complete list of all working dates from
            the project start date and end date"""
        current_date = self.project_start_date
        data = []
        while current_date <= self.project_end_date:
            exception = False
            for exception_time in exception_times:
                if exception_time.date == current_date:
                    data.append(exception_time)
                    exception = True
                    break
            if exception == False:
                day = find_weekday(current_date)
                times = self.default_days[str(day)]
                working_day = working_day_class(current_date, times)
                data.append(working_day)
            current_date = current_date + datetime.timedelta(days=1)
        return(data)
    
    def write_data_to_csv(self, filename):
        """Writes the data to a .csv file"""
        file_string = ''
        for datum in self.data:
            line = "{}, {}\n".format(datum.date, datum.total_time)
            file_string += line
        file = open(filename, 'w')
        file.write(file_string)
        file.close()

class task_class:
    """A class for using methods of comprehending tasks."""
    def __init__(self, name, duration_string):
        self.name = name
        self.duration_string = duration_string
        self.total_hours = self.translate_duration_string()
    
    def __repr__(self):
        return_string = "{}: {}".format(self.name, self.total_hours)
        return(return_string)
    
    def translate_duration_string(self):
        """Translates self.duration_string into number of hours"""
        split_string = self.duration_string.split('T')[1]
        hours = float(split_string.split('H')[0])
        split_string = split_string.split('H')[1]
        minutes = float(split_string.split('M')[0])
        split_string = split_string.split('M')[1]
        seconds = float(split_string.split('S')[0])
        total_hours = hours + minutes/60 + seconds/60/60
        return(total_hours)
        

def import_task_duration_csv_data(filename):
    """Imports task duration data for a project from a properly  formatted.csv file.
        HACK assumes a very specific format for the csv file"""
    
    file = open(filename)
    data_reader = csv.reader(file, delimiter=',')
    
    tasks = []
    for row in data_reader:
        task = task_class(name=row[0], duration_string=row[1])
        tasks.append(task)
    return(tasks)

def write_task_data_to_csv(taks, filename):
    """Writes the task data to a .csv file"""
    file_string = ''
    for task in tasks:
        line = "{}, {}\n".format(task.name, task.total_hours)
        file_string += line
    file = open(filename, 'w')
    file.write(file_string)
    file.close()

tasks = import_task_duration_csv_data('task_hours_2014_04_23.csv')
write_task_data_to_csv(tasks, 'task_hours_complete_2014_04_23.csv')
#return_values = import_working_time_csv_data("Neptune_Spear_Phase1_2014_04_23.csv")
#default_days = return_values[0]
#exception_times = return_values[1]
#project_start_date = datetime.date(year=2014, month=4, day=1)
#project_end_date = datetime.date(year=2014, month=5, day=31)
#kevin_calendar = resource_calendar_class(resource_name="Kevin", project_start_date=project_start_date,
#                                         project_end_date=project_end_date, default_days=default_days,
#                                         exception_times=exception_times)
#kevin_calendar.write_data_to_csv('kevin_data_2014_04_23.csv')