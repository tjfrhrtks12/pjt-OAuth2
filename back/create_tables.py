from config import engine
from models import AttendanceType, AttendanceReason, Attendance, MonthlyAttendance, YearlyAttendance, CalendarEvent

def create_attendance_type_table():
    """AttendanceType 테이블 생성"""
    try:
        AttendanceType.__table__.create(engine, checkfirst=True)
        print("✅ AttendanceType 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ AttendanceType 테이블 생성 실패: {e}")
        return False

def create_attendance_reason_table():
    """AttendanceReason 테이블 생성"""
    try:
        AttendanceReason.__table__.create(engine, checkfirst=True)
        print("✅ AttendanceReason 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ AttendanceReason 테이블 생성 실패: {e}")
        return False

def create_attendance_table():
    """Attendance 테이블 생성"""
    try:
        Attendance.__table__.create(engine, checkfirst=True)
        print("✅ Attendance 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ Attendance 테이블 생성 실패: {e}")
        return False

def create_monthly_attendance_table():
    """MonthlyAttendance 테이블 생성"""
    try:
        MonthlyAttendance.__table__.create(engine, checkfirst=True)
        print("✅ MonthlyAttendance 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ MonthlyAttendance 테이블 생성 실패: {e}")
        return False

def create_yearly_attendance_table():
    """YearlyAttendance 테이블 생성"""
    try:
        YearlyAttendance.__table__.create(engine, checkfirst=True)
        print("✅ YearlyAttendance 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ YearlyAttendance 테이블 생성 실패: {e}")
        return False

def create_calendar_event_table():
    """CalendarEvent 테이블 생성"""
    try:
        CalendarEvent.__table__.create(engine, checkfirst=True)
        print("✅ CalendarEvent 테이블 생성 완료!")
        return True
    except Exception as e:
        print(f"❌ CalendarEvent 테이블 생성 실패: {e}")
        return False

if __name__ == "__main__":
    create_attendance_type_table()
    create_attendance_reason_table()
    create_attendance_table()
    create_monthly_attendance_table()
    create_yearly_attendance_table()
    create_calendar_event_table() 