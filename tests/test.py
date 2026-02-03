import src.python.cfs_simp as cfs

f = open("testfiles/td1.txt", "r")
lines = f.readlines()

print(cfs.cfs_simp(lines))