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
                time_jump_errors.append(f"Time going backwards detected: {last_time} -> {current_time}")
            last_time = current_time
    return time_jump_errors

def detect_missing_samples(log_lines):
    expected_ids = {}
    missing_samples = []
    time_threshold = 0.02  # 20 milliseconds

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

        # Check for the pair
        pair_id = can_id[:-1] + ('1' if can_id[-1] == '2' else '2')
        if pair_id in expected_ids:
            expected_ids.pop(pair_id)  # Remove the pair from expected IDs

    return missing_samples

def main(filename, output_filename):
    log_lines = parse_log_file(filename)
    
    time_jump_errors = check_time_jumps(log_lines)
    missing_samples = detect_missing_samples(log_lines)

    with open(output_filename, 'w') as output_file:
        if time_jump_errors:
            output_file.write("Time jump errors detected:\n")
            for error in time_jump_errors:
                output_file.write(f"{error}\n")
        if missing_samples:
            output_file.write("Missing samples detected:\n")
            for sample in missing_samples:
                output_file.write(f"{sample}\n")

    total_time_jumps = len(time_jump_errors)
    total_missing_samples = len(missing_samples)
    
    print(f"Total time jump errors detected: {total_time_jumps}")
    print(f"Total missing samples detected: {total_missing_samples}")
    print(f"Detailed report saved to {output_filename}")

if __name__ == "__main__":
    log_filename = 'VBOX0001_CANLog.ASC'  # Replace with your log file name
    output_filename = 'log_analysis_report.txt'  # Output file name for detailed report
    main(log_filename, output_filename)
