
with open("kata_dasar.txt", "r") as f:
    kumpul = f.readlines()
kumpul = [x[:-1] for x in kumpul]
words = [x for x in kumpul if not len(x) < 4 and not "-" in x]

with open("kata_4+.txt", "w") as f:
    for word in words:
        f.writelines(word)
        f.writelines("\n")