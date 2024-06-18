import re

def parse_log_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Skip the header lines
    log_start_index = 0
    for i, line in enumerate(lines):
        if not line.startswith('//') and not line.startswith('date') and not line.startswith('base') and not line.startswith('no internal events logged'):
            log_start_index = i
            break

    # Parse the log lines
    log_lines = [line.strip() for line in lines[log_start_index:]]
    return log_lines

def check_time_jumps(log_lines):
    last_time = None
    time_jump_errors = []
    for line in log_lines:
        match = re.match(r'(\d+\.\d+)', line)
        if match:
            current_time = float(match.group(1))
            if last_time is not None and current_time < last_time:
                time_jump_errors.append(f"Time jump detected: {last_time} -> {current_time}")
            last_time = current_time
    return time_jump_errors

def detect_missing_samples(log_lines):
    expected_ids = {}
    missing_samples = []
    time_threshold = 0.2  # 200 milliseconds

    for line in log_lines:
        parts = line.split()
        timestamp = float(parts[0])
        can_id = parts[4]

        if can_id not in expected_ids:
            expected_ids[can_id] = timestamp
        else:
            expected_timestamp = expected_ids[can_id] + time_threshold
            if timestamp > expected_timestamp:
                missing_samples.append(f"Missing sample detected for {can_id} around {expected_timestamp}")
            expected_ids[can_id] = timestamp
    return missing_samples

def main(filename):
    log_lines = parse_log_file(filename)
    
    time_jump_errors = check_time_jumps(log_lines)
    if time_jump_errors:
        print("Time jump errors:")
        for error in time_jump_errors:
            print(error)
    else:
        print("No time jump errors detected.")
    
    missing_samples = detect_missing_samples(log_lines)
    if missing_samples:
        print("Missing samples:")
        for sample in missing_samples:
            print(sample)
    else:
        print("No missing samples detected.")

if __name__ == "__main__":
    log_filename = 'VBOX0001_CANLog.ASC'  # Replace with your log file name
    main(log_filename)
