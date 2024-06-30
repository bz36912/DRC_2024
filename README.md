# DRC_2024
Droid Race Competition for UQMARS Team 2 2024

The instruction are at documentations/DRC_2024_plan.docx
There are example codes under /example_code. These codes are NOT perfect.
Don't overwrite the example code. Write your code in the relevant files in the repo's home directory

## To run the code in the example_code folder:
you need to change the explorer/current directory to /example_code
On vsCode, go File/Open Folder, then select example_code

## Notes on power bank
Silver: 9V output is broken.
    Does not have issues with sleeping too early
Blue: Can supply 9V but not 100% consistent, so takes multiple attempts to get into 9V
    Keeps on sleeping (so use it to power the motors, which draws substantial current)
    USB port is a bit loose, so the connection is not perfect.
Black: 9V works and is currently the most consistent.
    The power button cannot be pressed when drawing power.