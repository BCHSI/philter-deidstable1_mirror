# take full notes csv notes file and read first 1000 lines from it

import re
fin = open("notes-full.csv")
fout = open("notes-mini.txt", "w")

a = 0
while a < 1000:
    fout.write(fin.readline())
    a += 1

fin.close()
fout.close()
