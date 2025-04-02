from datetime import datetime

def parse_sms(message: str):
    """Parse SMS to extract start_time, end_time, and reason."""
    try:
        parts = message.split()
        if parts[0].lower() != "offline":
            return None
        
        start_time = datetime.strptime(f"{parts[1]} {parts[2]}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{parts[1]} {parts[3]}", "%Y-%m-%d %H:%M")
        reason = " ".join(parts[4:]) if len(parts) > 4 else None
        
        return {
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason
        }
    except Exception as e:
        print(f"SMS parsing failed: {str(e)}")
        return None
