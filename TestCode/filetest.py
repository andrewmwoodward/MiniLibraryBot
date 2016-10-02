with open('numberofbooks.txt') as f:
    a = f.read()

remainingBooks = int(a)

remainingBooks += 1

print remainingBooks



with open('numberofbooks.txt', 'w') as f:
    f.write(str(remainingBooks))
