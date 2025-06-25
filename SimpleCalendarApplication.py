from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

class Event:
    def __init__(self, title: str, start_time: datetime, end_time: datetime):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    def overlaps_with(self, other: 'Event') -> bool:
        return (self.start_time < other.end_time and self.end_time > other.start_time)

class Calendar:
    def __init__(self):
        self.events: Dict[date, List[Event]] = {}

    def add_event(self, title: str, start_time: datetime, end_time: datetime) -> bool:
        if start_time >= end_time:
            print("Error: End time must be after start time")
            return False

        new_event = Event(title, start_time, end_time)
        event_date = start_time.date()

        if event_date not in self.events:
            self.events[event_date] = []

        # Check for overlaps with existing events
        for event in self.events[event_date]:
            if event.overlaps_with(new_event):
                print(f"Error: Event overlaps with '{event.title}'")
                return False

        self.events[event_date].append(new_event)
        # Sort events by start time
        self.events[event_date].sort(key=lambda x: x.start_time)
        return True

    def get_events_for_day(self, day: date) -> List[Event]:
        return self.events.get(day, [])

    def get_remaining_events_for_day(self, day: date) -> List[Event]:
        now = datetime.now()
        if day != now.date():
            return self.get_events_for_day(day)
        
        return [event for event in self.events.get(day, []) if event.end_time > now]

    def find_next_available_slot(self, duration: timedelta, day: date = None) -> Optional[datetime]:
        if day is None:
            day = date.today()

        if day not in self.events or not self.events[day]:
            return datetime.combine(day, datetime.min.time())

        # Check before first event
        first_event = self.events[day][0]
        available_start = datetime.combine(day, datetime.min.time())
        available_end = first_event.start_time
        if (available_end - available_start) >= duration:
            return available_start

        # Check between events
        for i in range(len(self.events[day]) - 1):
            current_event = self.events[day][i]
            next_event = self.events[day][i + 1]
            available_start = current_event.end_time
            available_end = next_event.start_time
            if (available_end - available_start) >= duration:
                return available_start

        # Check after last event
        last_event = self.events[day][-1]
        available_start = last_event.end_time
        available_end = datetime.combine(day, datetime.max.time())
        if (available_end - available_start) >= duration:
            return available_start

        return None

def print_events(events: List[Event]):
    if not events:
        print("No events found")
        return
    
    for i, event in enumerate(events, 1):
        print(f"{i}. {event}")

def parse_time(time_str: str, day: date) -> Optional[datetime]:
    try:
        hour, minute = map(int, time_str.split(':'))
        return datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute)
    except (ValueError, AttributeError):
        print("Invalid time format. Use HH:MM")
        return None

def parse_date(date_str: str) -> Optional[date]:
    if date_str.lower() == 'today':
        return date.today()
    if date_str.lower() == 'tomorrow':
        return date.today() + timedelta(days=1)
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD or 'today'/'tomorrow'")
        return None

def main():
    calendar = Calendar()
    
    # Add some sample events
    today = date.today()
    calendar.add_event("Morning Meeting", 
                      datetime.combine(today, datetime.strptime("09:00", "%H:%M").time()), 
                      datetime.combine(today, datetime.strptime("10:00", "%H:%M").time()))
    calendar.add_event("Lunch", 
                      datetime.combine(today, datetime.strptime("12:30", "%H:%M").time()), 
                      datetime.combine(today, datetime.strptime("13:30", "%H:%M").time()))
    calendar.add_event("Project Review", 
                      datetime.combine(today, datetime.strptime("14:00", "%H:%M").time()), 
                      datetime.combine(today, datetime.strptime("15:30", "%H:%M").time()))
    
    print("Welcome to Simple Calendar Application!")
    print("Available commands: add, list, remaining, find, exit")
    
    while True:
        try:
            command = input("> ").strip().lower().split()
            if not command:
                continue
                
            if command[0] == "add":
                title = input("Event title: ")
                date_str = input("Date (YYYY-MM-DD or 'today'/'tomorrow'): ")
                event_date = parse_date(date_str)
                if not event_date:
                    continue
                    
                start_time = input("Start time (HH:MM): ")
                start_dt = parse_time(start_time, event_date)
                if not start_dt:
                    continue
                    
                end_time = input("End time (HH:MM): ")
                end_dt = parse_time(end_time, event_date)
                if not end_dt:
                    continue
                    
                if calendar.add_event(title, start_dt, end_dt):
                    print("Event added successfully")
                    
            elif command[0] == "list":
                date_str = input("Enter date (YYYY-MM-DD or 'today'/'tomorrow'): ")
                event_date = parse_date(date_str)
                if event_date:
                    events = calendar.get_events_for_day(event_date)
                    print(f"\nEvents for {event_date}:")
                    print_events(events)
                    
            elif command[0] == "remaining":
                date_str = input("Enter date (YYYY-MM-DD or 'today'/'tomorrow'): ")
                event_date = parse_date(date_str)
                if event_date:
                    events = calendar.get_remaining_events_for_day(event_date)
                    print(f"\nRemaining events for {event_date}:")
                    print_events(events)
                    
            elif command[0] == "find":
                duration = input("Enter duration in minutes: ")
                try:
                    duration_min = int(duration)
                    if duration_min <= 0:
                        print("Duration must be positive")
                        continue
                        
                    duration_td = timedelta(minutes=duration_min)
                    date_str = input("Enter date (YYYY-MM-DD or 'today'/'tomorrow'), leave blank for today: ")
                    event_date = parse_date(date_str) if date_str else date.today()
                    
                    if event_date:
                        slot = calendar.find_next_available_slot(duration_td, event_date)
                        if slot:
                            print(f"Next available slot: {slot.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            print("No available slot found for the requested duration")
                except ValueError:
                    print("Invalid duration. Please enter a number")
                    
            elif command[0] == "exit":
                break
                
            else:
                print("Unknown command. Available commands: add, list, remaining, find, exit")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()