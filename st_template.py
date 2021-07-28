tempDir = ""

sambaWork = "//username:password@hostname/Sharedfolder/"
sambaHome = "//username:password@hostname/Sharedfolder/"

ruleout = [
    '/Users/USERNAME/Pictures/Photos Library.photoslibrary',
    tempDir,
]

workloads = [
    ["/Users/username/WorkFolder", "WorkFolder", sambaHome],
    ["/Users/username/WorkFolder", "WorkFolder", sambaWork],
    ["/Users/username/WorkFolder", "/Volumes/ExternalDrive/WorkFolder"],
]
