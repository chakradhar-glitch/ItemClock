def individual_clock_in_serial(clock_in):
    return {
        "id": str(clock_in["_id"]),
        "email": clock_in['email'],
        "location":clock_in['location'],
        'insert_datetime': clock_in['insert_datetime'].strftime("%Y-%m-%d %H:%M:%S")
    }


def list_clock_in_serial(clock_ins):
    return [individual_clock_in_serial(clock_in) for clock_in in clock_ins]
