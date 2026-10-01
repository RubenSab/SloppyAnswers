import requests
from bs4 import BeautifulSoup as bs

def _links_from_page(page_index: int) -> list[str]:
    url = f'https://areasosta.com/faq/?page={page_index}'
    soup = bs(requests.get(url).content, 'lxml')
    links = [
        f'https://areasosta.com{a.get("href")}' for a in soup.find_all('a')
        if a.get('href').startswith('/faq') \
        and "page=" not in a.get('href')
    ]
    return links

def write_questions(start_i: int, end_i: int, file:str) -> bool:
    with open(file, "a") as f:
        for i in range(start_i, end_i+1):
            f.write('\n'.join(_links_from_page(i))+'\n')
            print(f'{i} done')

def fetch_questions(query: str, n: int, file: str) -> list[str]:
    keywords = [word for word in query.replace("'", ' ').split() if len(word) > 1]
    results = []
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            line_words = line.split('/')[-1].split('-')
            relevance = len([word for word in keywords if word in line_words])
            if relevance > 0:
                results.append((relevance, line))
    sorted_links = [link for relevance, link in sorted(results, reverse=True)]
    return sorted_links[:(min(len(sorted_links), n))]

def get_question_from_answer(url: str) -> list[str]:
    soup = bs(requests.get(url).content, 'lxml')
    return [inner_span.get_text() for inner_span in soup.select('span > span')][0].strip()

if __name__=='__main__':
    print('Benvenuto su SloppyAnswers! cerca "quit" se vuoi chiudere')
    while True:
        query = input('\n--------------------\nCerca: ')
        if query == 'quit':
            break
        n = int(input('N. di risultati: '))
        questions = fetch_questions(query, n, 'questions.txt')
        print('\n', *[
            f'{i+1}. {question.split("/")[-1].replace('-', ' ')}\n' for i, question in enumerate(fetch_questions(query, n, 'questions.txt'))
        ], sep='')
        if len(questions) > 0:
            choice = min(int(input(f'\nScegli una domanda: '))-1, len(questions))
            print(f'\nDa {questions[choice]} :\n\n{get_question_from_answer(questions[choice]).replace(". ", ".\n")}')
