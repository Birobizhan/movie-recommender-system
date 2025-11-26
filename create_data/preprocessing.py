all_films = []

with open('with_review.txt', 'r', encoding='utf-8') as file_1:
    content = file_1.readlines()
    for i in content:
        all_films.append(i.rstrip())

with open('all_films.txt', 'r', encoding='utf-8') as file_2:
    content = file_2.readlines()
    for i in content:
        all_films.append(i.rstrip())

print(len(all_films))
all_films = list(set(all_films))
print(len(all_films))

with open('films_for_review.txt', 'w', encoding='utf-8') as reviews:
    for i in all_films:
        reviews.write(f'{i}\n')
