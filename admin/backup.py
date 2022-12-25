
def createattendance(user,shift,num_of_days=30):
    shift_start_hour =shift.start_time.hour
    shift_start_minute = shift.start_time.minute
    shift_start_seconds = shift.start_time.second
    shift_end_hour =shift.end_time.hour
    shift_end_minute = shift.end_time.minute
    shift_end_seconds = shift.end_time.second    
    current_time = datetime.datetime.now()
    created_attendances = []
    if current_time.weekday() == shift.day_num and current_time.time() < shift.start_time:
        shift_year = current_time.date().year
        shift_month =current_time.date().month
        shift_start_day =current_time.date().day
        start_date_time = datetime.datetime(shift_year,shift_month,shift_start_day,shift_start_hour,shift_start_minute,shift_start_seconds)
        end_date_time =  datetime.datetime(shift_year,shift_month,shift_start_day,shift_end_hour,shift_end_minute,shift_end_seconds)        
        attendance,created = Attendance.objects.get_or_create(user=user,shift=shift,start_date_time=start_date_time,end_date_time=end_date_time)
        created_attendances.append(attendance)
    done_creating = True
    attendance_count = 0
    day_count = 1
    while done_creating:
        next_shift_day = datetime.datetime.today()+datetime.timedelta(days=day_count)
        if next_shift_day.weekday() == shift.day_num:
            shift_year = next_shift_day.date().year
            shift_month =next_shift_day.date().month
            shift_start_day =next_shift_day.date().day
            start_date_time = datetime.datetime(shift_year,shift_month,shift_start_day,shift_start_hour,shift_start_minute,shift_start_seconds)
            end_date_time =  datetime.datetime(shift_year,shift_month,shift_start_day,shift_end_hour,shift_end_minute,shift_end_seconds)
            attendance,created = Attendance.objects.get_or_create(user=user,shift=shift,start_date_time=start_date_time,end_date_time=end_date_time)
            attendance_count+=1
            attendance.save()
            created_attendances.append(attendance)
            if attendance_count >= num_of_days:
                done_creating = False
        day_count+=1
    return created_attendances

