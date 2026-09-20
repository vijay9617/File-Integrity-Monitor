# File Integrity Monitoring (FIM) Tool

A Python-based File Integrity Monitoring tool that uses SHA-256
cryptographic hashing to detect unauthorized changes to files.

## Features

- SHA-256 file hashing
- Trusted baseline creation
- Continuous file monitoring
- Modified file detection
- Deleted file detection
- Newly added file detection
- Configurable monitoring interval
- Command-line interface

## How It Works

1. A trusted baseline is created containing SHA-256 hashes of monitored files.
2. The tool periodically calculates the current hashes.
3. Current hashes are compared with the trusted baseline.
4. The tool detects:
   - Modified files
   - Deleted files
   - Newly added files

## Technologies

- Python 3
- Kali Linux
- SHA-256
- `hashlib`
- `pathlib`
- `argparse`

## Usage

1Create a test directory:

```bash
mkdir Protectedfiles
echo "This is my test file" > Protectedfiles/test.txt
Create the baseline:
```

2. Create the baseline

Create a trusted baseline containing the SHA-256 hash of the monitored files:

```bash
python3 fim-1.py baseline Protectedfiles
```
3. Start monitoring
Start continuous file integrity monitoring:
```bash
python3 fim-1.py monitor Protectedfiles --interval 5
```
The tool checks the files every 5 seconds and compares their current SHA-256 hashes with the trusted baseline.
If no changes are detected:
```bash
[OK] No integrity changes detected.
```
Press Ctrl+C to stop monitoring.
4. Modify a file
Change the contents of the monitored file:
```bash
echo "hacked" > Protectedfiles/test.txt
```
The tool detects the changed SHA-256 hash:
```bash
FILE INTEGRITY ALERT

[MODIFIED]
  - test.txt
```
5. Delete a file
Delete the monitored file:
``` bash
rm Protectedfiles/test.txt
```
The tool detects that the file is no longer present:
```bash
FILE INTEGRITY ALERT

[DELETED]
  - test.txt
```
6. Add a new file
Create a new file inside the monitored directory:
```bash
echo "new file" > Protectedfiles/new.txt
```
The tool detects the newly added file:
```bash
FILE INTEGRITY ALERT

[ADDED]
  - new.txt
```
7. Test multiple changes
The tool can detect multiple changes at the same time
```bash
rm Protectedfiles/test.txt
echo "new file" > Protectedfiles/new.txt
```
The tool reports:
```bash
FILE INTEGRITY ALERT

[DELETED]
  - test.txt

[ADDED]
  - new.txt
```
## Security Concept

File Integrity Monitoring helps identify unauthorized changes to important files by comparing their current cryptographic hashes against a previously trusted baseline.

## Future Improvements

- Timestamped security logs
- Alert deduplication
- Email notifications
- Secure baseline storage
- Process and user information
- Web dashboard
## Author

Vijay B
